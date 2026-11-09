import unittest
from pathlib import Path

import pandas as pd

from utils.data import (
    ZAGREB_REGION,
    _canonical_occupation,
    _extract_category,
    _title_occupation_override,
    build_dashboard_data,
    calculate_pressure_index,
    canonical_region,
    combined_region,
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

    def test_extracts_category_before_truncated_next_field(self):
        self.assertEqual(
            _extract_category("Kategorija: ZDRAVSTVO, SOCIJALNA SKRB, NJEGA, Ro"),
            "ZDRAVSTVO, SOCIJALNA SKRB, NJEGA",
        )

    def test_preserves_categories_not_in_occupation_feed(self):
        category = "USLUGE U KUĆI, KOMUNALNE USLUGE I OSTALA ZANIMANJA"
        self.assertEqual(_canonical_occupation(category, []), category)

    def test_does_not_guess_ambiguous_truncated_category(self):
        self.assertEqual(
            _canonical_occupation(
                "STRUČNJACI",
                [
                    "STRUČNJACI U PROMETU",
                    "STRUČNJACI ZA ELEKTROTEHNIKU",
                ],
            ),
            "Nerazvrstano",
        )

    def test_normalizes_clear_job_titles_but_not_veterinary_doctors(self):
        self.assertEqual(
            _title_occupation_override("DOKTOR/DOKTORICA MEDICINE"),
            "ZDRAVSTVO, SOCIJALNA SKRB, NJEGA",
        )
        self.assertEqual(
            _title_occupation_override("DOKTOR VETERINARSKE MEDICINE"),
            None,
        )
        self.assertEqual(
            _title_occupation_override("KERAMIČAR/KERAMIČARKA"),
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


class DashboardDataIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_dashboard_data(Path(__file__).resolve().parents[1])

    def test_reads_recent_dzs_labor_table(self):
        self.assertIn("2026", self.data.national_labor.iloc[-1]["razdoblje"])

    def test_hzz_classification_covers_at_least_eighty_percent_of_snapshot(self):
        classified_share = (
            self.data.vacancies["zanimanje"] != "Nerazvrstano"
        ).mean()
        self.assertGreaterEqual(classified_share, 0.8)

    def test_preserves_and_normalizes_example_listing_categories(self):
        ceramician = self.data.vacancies.loc[
            self.data.vacancies["naziv_oglasa"].str.contains(
                "KERAMIČAR", case=False, na=False
            )
        ]
        self.assertIn(
            "GRAĐEVINARI, ARHITEKTI, GEODETE",
            ceramician["zanimanje"].tolist(),
        )
        self.assertIn("Pravilo iz naziva oglasa", ceramician["izvor_kategorije"].tolist())

        doctors = self.data.vacancies.loc[
            self.data.vacancies["naziv_oglasa"].str.contains(
                "DOKTOR.*MEDICINE", case=False, na=False
            )
        ]
        self.assertIn("ZDRAVSTVO, SOCIJALNA SKRB, NJEGA", doctors["zanimanje"].tolist())


if __name__ == "__main__":
    unittest.main()
