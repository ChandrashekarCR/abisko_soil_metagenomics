import pandas as pd
import pytest

from read_taxonomy import Taxonomy


def test_read_dataframe_drops_rows_without_classification(gtdbtk_tsv):
    tax = Taxonomy(str(gtdbtk_tsv))
    df = tax.read_dataframe()

    assert len(df) == 2
    assert "bin_missing" not in df["user_genome"].values


def test_convert_to_taxonomy_columns_strips_prefixes(gtdbtk_tsv):
    tax = Taxonomy(str(gtdbtk_tsv))
    df = tax.convert_to_taxonomy_columns().replace("", "Unclassified")

    assert list(df.columns) == ["bin", "domain", "phylum", "class", "order", "family", "genus"]
    assert df.loc[df["bin"] == "bin_1", "domain"].item() == "Bacteria"
    assert df.loc[df["bin"] == "bin_1", "phylum"].item() == "Proteobacteria"
    assert df.loc[df["bin"] == "bin_2", "genus"].item() == "Methanobacterium"


def test_read_genome_binning_converts_to_rsa(bins_tsv):
    tax = Taxonomy("unused")
    df = tax.read_genome_binning(str(bins_tsv), convert_to_rsa=True)

    assert list(df.columns) == ["bin", "Depth 1 TOP", "Depth 2 BOTTOM"]
    assert df["Depth 1 TOP"].sum() == pytest.approx(1.0)
    assert df["Depth 2 BOTTOM"].sum() == pytest.approx(1.0)
    assert df.loc[df["bin"] == "bin_1", "Depth 1 TOP"].item() == pytest.approx(0.25)
    assert df.loc[df["bin"] == "bin_2", "Depth 1 TOP"].item() == pytest.approx(0.75)


def test_create_taxonomic_abundance_plot_writes_png(gtdbtk_tsv, bins_tsv, tmp_path):
    tax = Taxonomy(str(gtdbtk_tsv))
    tax_df = tax.convert_to_taxonomy_columns().replace("", "Unclassified")
    bin_df = tax.read_genome_binning(str(bins_tsv), convert_to_rsa=True)
    merged_df = pd.merge(tax_df, bin_df, on="bin", how="outer")
    for col in ["domain", "phylum", "class", "order", "family", "genus"]:
        merged_df[col] = merged_df[col].fillna("Unclassified")

    output_dir = tmp_path / "plots"
    tax.create_taxonomic_abundance_plot(merged_df, "phylum", output_dir=str(output_dir), layer_filter="TOP")

    assert (output_dir / "phylum_top.png").exists()
