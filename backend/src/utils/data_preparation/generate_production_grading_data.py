#!/usr/bin/env python3
"""
Script to generate complete production data SQL file.
This script creates INSERT statements for both grading companies and their grades
in a single file for production deployment.
"""

import sys
from pathlib import Path
from uuid import uuid4


class ProductionDataGenerator:
    """Generator for complete production data (companies + grades)."""

    def __init__(self):
        """Initialize the generator."""
        self.company_uuids = {}  # Will store mapping of short_name to UUID

    def generate_companies_data(self) -> tuple[str, dict[str, str]]:
        """Generate SQL for grading companies and return company UUID mapping.

        Returns:
            tuple: (SQL content, dict mapping short_name to UUID)
        """

        # Standard grading companies data
        companies_data = [
            {
                "name": "Professional Coin Grading Service",
                "short_name": "PCGS",
                "country": "USA",
                "website": "https://www.pcgs.com",
                "cert_url_pattern": "https://www.pcgs.com/cert/{cert_number}",
                "supported_types": "coins",
                "is_active": True,
            },
            {
                "name": "Numismatic Guaranty Corporation",
                "short_name": "NGC",
                "country": "USA",
                "website": "https://www.ngccoin.com",
                "cert_url_pattern": "https://www.ngccoin.com/certlookup/{cert_number}/{grade}/",
                "supported_types": "coins",
                "is_active": True,
            },
            {
                "name": "ANACS",
                "short_name": "ANACS",
                "country": "USA",
                "website": "https://www.anacs.com",
                "cert_url_pattern": "https://portal.anacs.com/Verify/CertVerification.aspx?cert={cert_number}",
                "supported_types": "coins",
                "is_active": True,
            },
            {
                "name": "Independent Coin Graders",
                "short_name": "ICG",
                "country": "USA",
                "website": "https://www.icgcoin.com",
                "cert_url_pattern": "https://www.icgcoin.com/load_SNSearch.php?sn={cert_number}",
                "supported_types": "coins",
                "is_active": True,
            },
            {
                "name": "Certified Acceptance Corporation",
                "short_name": "CAC",
                "country": "USA",
                "website": "https://www.caccoins.com",
                "cert_url_pattern": "https://www.caccoins.com/verification/{cert_number}",
                "supported_types": "coins",
                "is_active": True,
            },
        ]

        # Generate SQL content
        sql_content = """-- Production grading companies
-- Total companies: 5

INSERT INTO grading_companies (
    id, name, short_name, country, website,
    cert_url_pattern, supported_types, is_active
) VALUES
"""

        values = []
        company_uuids = {}

        for company in companies_data:
            # Generate UUID for this company
            company_id = str(uuid4())

            # Escape single quotes in values
            name = company["name"].replace("'", "''")
            short_name = company["short_name"].replace("'", "''")
            country = company["country"].replace("'", "''")
            website = company["website"].replace("'", "''")
            cert_url_pattern = company["cert_url_pattern"].replace("'", "''")
            supported_types = company["supported_types"].replace("'", "''")
            is_active = "true" if company["is_active"] else "false"

            # Store UUID mapping
            company_uuids[company["short_name"]] = company_id

            value = (
                f"('{company_id}', '{name}', '{short_name}', '{country}', "
                f"'{website}', '{cert_url_pattern}', '{supported_types}', {is_active})"
            )
            values.append(value)

        sql_content += ",\n".join(values) + ";\n\n"

        # Store for grades generation
        self.company_uuids = company_uuids

        return sql_content, company_uuids

    def add_modifiers(self, base_grades: list[str]) -> list[str]:
        """Add modifiers to base grades."""
        result = []
        for g in base_grades:
            result.append(g)
            result.append(f"{g}+")
            result.append(f"{g}★")
            result.append(f"{g}+★")
        return result

    def generate_grades_for_company(self, company: dict) -> list[dict]:
        """Generate grades for a specific company."""
        # Modern coin grades (MS, PR/PF, AU, XF, VF, F, VG, G)
        mint_state_nums = [f"MS {i}" for i in range(60, 71)]
        mint_state_grades = self.add_modifiers(mint_state_nums)

        proof_nums_pf = [f"PF {i}" for i in range(60, 71)]
        ngc_proof_grades = self.add_modifiers(proof_nums_pf)

        proof_nums_pr = [f"PR {i}" for i in range(60, 71)]
        pcgs_proof_grades = self.add_modifiers(proof_nums_pr)

        about_uncirculated_base = ["AU 58", "AU 55", "AU 53", "AU 50"]
        about_uncirculated_grades = self.add_modifiers(about_uncirculated_base)

        extremely_fine_base = ["XF 45", "XF 40"]
        extremely_fine_grades = self.add_modifiers(extremely_fine_base)

        very_fine_base = ["VF 35", "VF 30", "VF 25", "VF 20"]
        very_fine_grades = self.add_modifiers(very_fine_base)

        fine_base = ["F 15", "F 12"]
        fine_grades = self.add_modifiers(fine_base)

        very_good_base = ["VG 10", "VG 8"]
        very_good_grades = self.add_modifiers(very_good_base)

        good_base = ["G 6", "G 4"]
        good_grades = self.add_modifiers(good_base)

        # Details grades
        details_grades = [
            "UNC DETAILS",
            "VF DETAILS",
            "AU DETAILS",
            "CLEANING",
            "CLEANED",
            "CORROSION",
            "DAMAGE",
            "DETAILS",
            "EDGE DAMAGE",
            "ENVIRONMENTAL DAMAGE",
            "GRAFFITI",
            "HARSH CLEANING",
            "HOLED",
            "HOLE FILLED",
            "IMPROPERLY CLEANED",
            "PLUGGED",
            "QUESTIONABLE COLOR",
            "SCRATCH",
            "SCRATCHED",
            "STAINED",
            "TOOLED",
            "WHIZZED",
            "ARTIFICIAL TONING",
            "BENT",
            "CHOP MARKS",
            "EXCESSIVE CARBON",
            "EXCESSIVE CORROSION",
            "FILING",
            "GROUND",
            "IMPROPERLY STORED",
            "MOUNTING DAMAGE",
            "MULTI-STRUCK",
            "NET",
            "PLANCHET CRACK",
            "PLANCHET FLAW",
            "POLISHED",
            "POST-MINT DAMAGE",
            "PRESS CRACKED",
            "ROUGH SURFACES",
            "SPOT",
            "SPOTTED",
            "SURFACE ENHANCEMENT",
            "SURFACE HAIRLINES",
            "TEST CUT",
            "VERDIGRIS",
        ]

        # Special grades
        special_grades = ["GENUINE", "AUTHENTIC"]

        # Ancient grades
        ancient_grades = [
            "Ch XF",
            "Ch VF",
            "Ch F",
            "Ch VG",
            "Ch G",
            "XF",
            "VF",
            "F",
            "VG",
            "G",
            "Fair",
            "Poor",
            "Superb",
            "Choice",
            "Fine",
            "Very Fine",
        ]

        # Proof designations
        proof_designations = [
            "PROOF",
            "DEEP CAMEO",
            "ULTRA CAMEO",
            "CAMEO",
            "REVERSE PROOF",
            "DCAM",
            "UCAM",
            "CAM",
        ]

        grades = []
        sort_order = 1
        company_id = company["id"]
        short_name = company["short_name"]

        # Add modern grades for PCGS, NGC, ANACS, ICG
        if short_name in ["PCGS", "NGC", "ANACS", "ICG"]:
            # Mint State
            for grade in mint_state_grades:
                grades.append(
                    {
                        "company_id": company_id,
                        "category": "modern",
                        "value": grade,
                        "sort_order": sort_order,
                    }
                )
                sort_order += 1

            # Proof grades - use PF for NGC, PR for PCGS/ANACS/ICG
            proof_grades = ngc_proof_grades if short_name == "NGC" else pcgs_proof_grades
            for grade in proof_grades:
                grades.append(
                    {
                        "company_id": company_id,
                        "category": "modern",
                        "value": grade,
                        "sort_order": sort_order,
                    }
                )
                sort_order += 1

            # Circulated grades
            for grade_list in [
                about_uncirculated_grades,
                extremely_fine_grades,
                very_fine_grades,
                fine_grades,
                very_good_grades,
                good_grades,
            ]:
                for grade in grade_list:
                    grades.append(
                        {
                            "company_id": company_id,
                            "category": "modern",
                            "value": grade,
                            "sort_order": sort_order,
                        }
                    )
                    sort_order += 1

        # Add details grades for all companies (including CAC)
        for grade in details_grades:
            grades.append(
                {
                    "company_id": company_id,
                    "category": "details",
                    "value": grade,
                    "sort_order": sort_order,
                }
            )
            sort_order += 1

        # Add special grades for all companies
        for grade in special_grades:
            grades.append(
                {
                    "company_id": company_id,
                    "category": "modern",
                    "value": grade,
                    "sort_order": sort_order,
                }
            )
            sort_order += 1

        # Add ancient grades for NGC (they grade ancient coins)
        if short_name == "NGC":
            for grade in ancient_grades:
                grades.append(
                    {
                        "company_id": company_id,
                        "category": "ancient",
                        "value": grade,
                        "sort_order": sort_order,
                    }
                )
                sort_order += 1

        # Add proof designations for all companies that do modern grading
        if short_name in ["PCGS", "NGC", "ANACS", "ICG"]:
            for grade in proof_designations:
                grades.append(
                    {
                        "company_id": company_id,
                        "category": "modern",
                        "value": grade,
                        "sort_order": sort_order,
                    }
                )
                sort_order += 1

        return grades

    def generate_grades_data(self, company_short_names: list[str]) -> str:
        """Generate SQL for grades for specified companies."""
        # Build companies list from our UUID mapping
        companies = []
        for short_name in company_short_names:
            if short_name in self.company_uuids:
                companies.append(
                    {
                        "id": self.company_uuids[short_name],
                        "short_name": short_name,
                        "name": f"Company {short_name}",  # This is just for display
                    }
                )
            else:
                print(f"Warning: Company '{short_name}' not found in generated companies")

        if not companies:
            raise ValueError(f"No companies found for: {company_short_names}")

        # Generate grades for each company
        all_grades = []
        for company in companies:
            company_grades = self.generate_grades_for_company(company)
            all_grades.extend(company_grades)

        # Generate SQL content
        companies_list = ", ".join([c["short_name"] for c in companies])
        sql_content = f"""-- Production grades for companies: {companies_list}
-- Total grades: {len(all_grades)}

"""

        # Add company information as comments
        for company in companies:
            sql_content += f"-- Company: {company['short_name']} (ID: {company['id']})\n"

        sql_content += "\nINSERT INTO grades (id, company_id, category, value, sort_order) VALUES\n"

        values = []
        for grade in all_grades:
            # Generate UUID for this grade
            grade_id = str(uuid4())

            # Escape single quotes in grade values
            escaped_value = grade["value"].replace("'", "''")
            value = (
                f"('{grade_id}', '{grade['company_id']}', "
                f"'{grade['category']}', '{escaped_value}', {grade['sort_order']})"
            )
            values.append(value)

        sql_content += ",\n".join(values) + ";\n"

        return sql_content

    def generate_complete_sql(self, company_short_names: list[str]) -> str:
        """Generate complete SQL with both companies and grades."""
        companies_sql, _ = self.generate_companies_data()
        grades_sql = self.generate_grades_data(company_short_names)

        return companies_sql + grades_sql


def main():
    """Main function to generate complete production data."""
    # Get company short names from command line arguments or use all
    if len(sys.argv) < 2:
        print("Usage: python generate_production_data.py [COMPANY1 COMPANY2 ...]")
        print("Example: python generate_production_data.py PCGS NGC")
        print("Available companies: PCGS, NGC, ANACS, ICG, CAC")
        print("If no companies specified, all will be included")
        company_names = ["PCGS", "NGC", "ANACS", "ICG", "CAC"]
    else:
        company_names = sys.argv[1:]

    # Create prepared_sql directory if it doesn't exist
    prepared_sql_dir = Path(__file__).parent / "prepared_sql"
    prepared_sql_dir.mkdir(exist_ok=True)

    # Output file - только один файл
    output_file = prepared_sql_dir / "production_grading_data.sql"

    try:
        generator = ProductionDataGenerator()

        print("Generating complete production data...")
        print("Companies: all (PCGS, NGC, ANACS, ICG, CAC)")
        print(f"Grades for: {company_names}")

        # Generate complete SQL
        complete_sql = generator.generate_complete_sql(company_names)

        # Get company UUIDs for display
        company_uuids = generator.company_uuids

        # Count grades from complete SQL
        grade_lines = [
            line
            for line in complete_sql.split("\n")
            if line.strip().startswith("('") and "', '" in line and "category" not in line
        ]
        grades_count = len(grade_lines)

        # Write only the complete file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(complete_sql)

        print("\nSUCCESS: Generated file:")
        print(f"  Complete data: {output_file}")

        print("\nStatistics:")
        print(f"  Companies: {len(company_uuids)}")
        print(f"  Grades: {grades_count}")

        print("\nCompany UUIDs:")
        for short_name, uuid in company_uuids.items():
            print(f"  {short_name}: {uuid}")

        print("\nDeployment:")
        print(f"  psql $DATABASE_URL < {output_file}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
