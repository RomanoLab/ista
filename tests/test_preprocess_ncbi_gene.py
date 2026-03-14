"""Tests for the NCBI Gene dbXrefs preprocessing script."""

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from comptox_ai.build.scripts.preprocess_ncbi_gene import (
    parse_dbxrefs,
    preprocess_gene_info,
)


class TestParseDbxrefs:
    """Test parse_dbxrefs on individual field values."""

    def test_all_three_xrefs(self):
        result = parse_dbxrefs("MIM:603369|HGNC:HGNC:1789|Ensembl:ENSG00000123080")
        assert result["MIM"] == "603369"
        assert result["HGNC"] == "HGNC:1789"
        assert result["Ensembl"] == "ENSG00000123080"

    def test_dash_means_no_xrefs(self):
        result = parse_dbxrefs("-")
        assert result["MIM"] == ""
        assert result["HGNC"] == ""
        assert result["Ensembl"] == ""

    def test_empty_string(self):
        result = parse_dbxrefs("")
        assert result == {"MIM": "", "HGNC": "", "Ensembl": ""}

    def test_only_mim(self):
        result = parse_dbxrefs("MIM:123456")
        assert result["MIM"] == "123456"
        assert result["HGNC"] == ""
        assert result["Ensembl"] == ""

    def test_only_hgnc(self):
        result = parse_dbxrefs("HGNC:HGNC:5432")
        assert result["HGNC"] == "HGNC:5432"
        assert result["MIM"] == ""
        assert result["Ensembl"] == ""

    def test_only_ensembl(self):
        result = parse_dbxrefs("Ensembl:ENSG00000099999")
        assert result["Ensembl"] == "ENSG00000099999"
        assert result["MIM"] == ""
        assert result["HGNC"] == ""

    def test_two_of_three(self):
        result = parse_dbxrefs("MIM:111111|Ensembl:ENSG00000000001")
        assert result["MIM"] == "111111"
        assert result["Ensembl"] == "ENSG00000000001"
        assert result["HGNC"] == ""

    def test_unknown_xref_types_ignored(self):
        result = parse_dbxrefs("AllianceGenome:HGNC:1|MIM:999")
        assert result["MIM"] == "999"
        assert result["HGNC"] == ""
        assert result["Ensembl"] == ""

    def test_whitespace_in_pairs(self):
        result = parse_dbxrefs(" MIM:100 | HGNC:HGNC:200 ")
        assert result["MIM"] == "100"
        assert result["HGNC"] == "HGNC:200"


class TestPreprocessGeneInfo:
    """Test end-to-end file preprocessing."""

    def _make_input(self, tmp_path, rows, header=None):
        if header is None:
            header = "tax_id\tGeneID\tSymbol\tdbXrefs\ttype_of_gene\tFull_name_from_nomenclature_authority"
        f = tmp_path / "gene_info.tsv"
        f.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
        return f

    def test_basic_preprocessing(self, tmp_path):
        inp = self._make_input(tmp_path, [
            "9606\t672\tBRCA1\tMIM:113705|HGNC:HGNC:1100|Ensembl:ENSG00000012048\tprotein-coding\tBRCA1 DNA repair",
            "9606\t7157\tTP53\tMIM:191170|HGNC:HGNC:11998|Ensembl:ENSG00000141510\tprotein-coding\tTumor protein p53",
        ])
        out = tmp_path / "output.tsv"
        n = preprocess_gene_info(inp, out)

        assert n == 2
        assert out.exists()

        with open(out, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["MIM"] == "113705"
        assert rows[0]["HGNC"] == "HGNC:1100"
        assert rows[0]["Ensembl"] == "ENSG00000012048"
        assert rows[1]["MIM"] == "191170"

    def test_missing_xrefs_produce_empty_columns(self, tmp_path):
        inp = self._make_input(tmp_path, [
            "9606\t100\tFOO\t-\tpseudo\tFoo gene",
        ])
        out = tmp_path / "output.tsv"
        preprocess_gene_info(inp, out)

        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))

        assert rows[0]["MIM"] == ""
        assert rows[0]["HGNC"] == ""
        assert rows[0]["Ensembl"] == ""

    def test_partial_xrefs(self, tmp_path):
        inp = self._make_input(tmp_path, [
            "9606\t200\tBAR\tEnsembl:ENSG00000000002\tncRNA\tBar gene",
        ])
        out = tmp_path / "output.tsv"
        preprocess_gene_info(inp, out)

        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))

        assert rows[0]["MIM"] == ""
        assert rows[0]["HGNC"] == ""
        assert rows[0]["Ensembl"] == "ENSG00000000002"

    def test_hash_header_normalised(self, tmp_path):
        """NCBI files sometimes start the header with '#'."""
        inp = self._make_input(
            tmp_path,
            ["9606\t1\tA\t-\tgene\tA gene"],
            header="#tax_id\tGeneID\tSymbol\tdbXrefs\ttype_of_gene\tFull_name_from_nomenclature_authority",
        )
        out = tmp_path / "output.tsv"
        preprocess_gene_info(inp, out)

        with open(out, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            assert reader.fieldnames is not None
            assert "tax_id" in reader.fieldnames
            rows = list(reader)

        assert rows[0]["tax_id"] == "9606"


class TestCLI:
    """Test the command-line interface."""

    def test_cli_invocation(self, tmp_path):
        inp = tmp_path / "input.tsv"
        inp.write_text(
            "tax_id\tGeneID\tSymbol\tdbXrefs\ttype_of_gene\tFull_name_from_nomenclature_authority\n"
            "9606\t672\tBRCA1\tMIM:113705\tprotein-coding\tBRCA1\n",
            encoding="utf-8",
        )
        out = tmp_path / "output.tsv"

        result = subprocess.run(
            [sys.executable, "-m", "comptox_ai.build.scripts.preprocess_ncbi_gene",
             "--input", str(inp), "--output", str(out)],
            capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent),
        )
        assert result.returncode == 0
        assert out.exists()
        assert "Preprocessed 1 rows" in result.stdout or "Preprocessed 1 row" in result.stdout
