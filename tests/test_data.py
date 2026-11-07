import unittest

import pandas as pd

from utils.data import (
    ZAGREB_REGION,
    calculate_pressure_index,
    _canonical_occupation,
    canonical_region,
    combined_region,
    _extract_category,
    parse_report_date,
)


class RegionHelpersTests(unittest.TestCase):
    def test_normalizes_hzz_and_dzs_region_names(self):
        self.assertEqual(
            canonical_region("DUBROVAČKO-NERETVANSKA"),
            "Dubrovačko-neretvanska županija",
        )
        self.assertEqual(
            canonical_region("Zagrebačka županija"),
            "Zagrebačka županija",
        )

    def test_combines_zagreb_for_mup_jurisdiction(self):
        self.assertEqual(combined_region("Grad Zagreb"), ZAGREB_REGION)
        self.assertEqual(combined_region("Zagrebačka"), ZAGREB_REGION)

    def test_parses_mup_date_formats(self):
        self.assertEqual(str(parse_report_date("31.3.2026")), "2026-03-31")
        self.assertEqual(str(parse_report_date("2025-30-4")), "2025-04-30")

    def test_extracts_truncated_category_and_maps_it_to_known_group(self):
        category = _extract_category(
            "Opis posla: rad na gradilištu, Kategorija: GRAĐEVINARI, "
            "ARHITEKTI, GEODETE, Rok za prij"
        )
        self.assertEqual(
            _canonical_occupation(
                category, ["GRAĐEVINARI, ARHITEKTI, GEODETE"]
            ),
            "GRAĐEVINARI, ARHITEKTI, GEODETE",
        )


class PressureIndexTests(unittest.TestCase):
    def test_index_ranks_regions_using_both_rates(self):
        regions = pd.DataFrame(
            {
                "regija": ["A", "B"],
                "stanovnici": [1000, 1000],
                "hzz_oglasi": [1, 3],
                "mup_dozvole": [3, 1],
            }
        )
        result = calculate_pressure_index(regions)
        self.assertAlmostEqual(result.iloc[0]["indeks_pritiska"], 50.0)
        self.assertAlmostEqual(result.iloc[1]["indeks_pritiska"], 50.0)


if __name__ == "__main__":
    unittest.main()
