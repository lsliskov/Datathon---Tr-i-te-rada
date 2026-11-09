import unittest
from pathlib import Path

import pandas as pd

from utils.data import (
    ZAGREB_REGION,
    _canonical_occupation,
    _extract_category,
    _title_occupation_fallback,
    _title_occupation_override,
    build_dashboard_data,
    calculate_regional_rates,
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

    def test_classifies_unambiguous_unclassified_job_titles(self):
        self.assertEqual(
            _title_occupation_fallback("KONOBAR/KONOBARICA"),
            "JEDNOSTAVNA PRODAJNA I USLUŽNA ZANIMANJA",
        )
        self.assertEqual(
            _title_occupation_fallback("ELEKTROINSTALATER/KA"),
            "GRAĐEVINARI, ARHITEKTI, GEODETE",
        )
        self.assertEqual(
            _title_occupation_fallback("OSOBNI ASISTENT/ICA"),
            "ZDRAVSTVO, SOCIJALNA SKRB, NJEGA",
        )
        self.assertEqual(
            _title_occupation_fallback("RADNIK/RADNICA U PROIZVODNJI"),
            "JEDNOSTAVNA GRAĐEVINSKA, PROIZVODNA I TRANSPORTNA ZANIMANJA",
        )
        self.assertIsNone(_title_occupation_fallback("MONTER/KA"))
        self.assertIsNone(_title_occupation_fallback("ASISTENT/ASISTENTICA"))


class RegionalRateTests(unittest.TestCase):
    def test_calculates_separate_rates_without_composite_index(self):
        regions = pd.DataFrame(
            {
                "regija": ["A", "B"],
                "stanovnici": [1000, 2000],
                "hzz_oglasi": [10, 30],
                "mup_dozvole": [20, 40],
            }
        )
        result = calculate_regional_rates(regions).set_index("regija")
        self.assertAlmostEqual(result.loc["A", "oglasi_na_1000"], 10.0)
        self.assertAlmostEqual(result.loc["B", "oglasi_na_1000"], 15.0)
        self.assertAlmostEqual(result.loc["A", "dozvole_na_1000"], 20.0)
        self.assertAlmostEqual(result.loc["B", "dozvole_na_1000"], 20.0)
        self.assertNotIn("indeks_pritiska", result.columns)
        self.assertNotIn("ocjena_potraznje", result.columns)


class DashboardDataIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_dashboard_data(Path(__file__).resolve().parents[1])

    def test_reads_recent_dzs_labor_table(self):
        self.assertIn("2026", self.data.national_labor.iloc[-1]["razdoblje"])

    def test_regional_occupation_counts_are_available(self):
        classified = self.data.occupations.loc[
            self.data.occupations["zanimanje"] != "Nerazvrstano"
        ]
        self.assertIn("regija", classified.columns)
        self.assertIn("zanimanje", classified.columns)
        self.assertIn("oglasi", classified.columns)
        self.assertGreater(classified["oglasi"].sum(), 0)

    def test_hzz_classification_covers_at_least_ninety_percent_of_snapshot(self):
        classified_share = (
            self.data.vacancies["zanimanje"] != "Nerazvrstano"
        ).mean()
        self.assertGreaterEqual(classified_share, 0.9)

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

        waiters = self.data.vacancies.loc[
            self.data.vacancies["naziv_oglasa"].str.contains(
                "KONOBAR", case=False, na=False
            )
        ]
        self.assertIn(
            "JEDNOSTAVNA PRODAJNA I USLUŽNA ZANIMANJA",
            waiters["zanimanje"].tolist(),
        )
        self.assertIn("Pravilo iz naziva oglasa", waiters["izvor_kategorije"].tolist())

    def test_quality_table_links_to_current_mup_and_dzs_sources(self):
        mup_source = self.data.quality.loc[
            self.data.quality["Izvor"] == "MUP", "Ponovno preuzimanje"
        ].iloc[0]
        population_source = self.data.quality.loc[
            self.data.quality["Što prikazuje"].str.contains("stanovništva"),
            "Ponovno preuzimanje",
        ].iloc[0]
        self.assertIn("data.gov.hr/ckan/dataset/", mup_source)
        self.assertIn("web.dzs.hr/PXWeb/api/v1/", population_source)


if __name__ == "__main__":
    unittest.main()
