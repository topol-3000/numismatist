"""Utility for loading SQL data files into test database."""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class SQLDataLoader:
    """Loads SQL INSERT statements from files into test database."""
    
    async def create_grading_companies_with_orm(self, session: AsyncSession):
        """Create grading companies using ORM and return them"""
        from models import GradingCompany
        
        # Hardcoded company data matching the SQL file
        companies_data = [
            {
                'name': 'Professional Coin Grading Service',
                'short_name': 'PCGS',
                'country': 'USA',
                'website': 'https://www.pcgs.com',
                'cert_url_pattern': 'https://www.pcgs.com/cert/{cert_number}',
                'supported_types': 'coins',
                'is_active': True
            },
            {
                'name': 'Numismatic Guaranty Corporation',
                'short_name': 'NGC',
                'country': 'USA',
                'website': 'https://www.ngccoin.com',
                'cert_url_pattern': 'https://www.ngccoin.com/certlookup/{cert_number}/{grade}/',
                'supported_types': 'coins',
                'is_active': True
            },
            {
                'name': 'ANACS',
                'short_name': 'ANACS',
                'country': 'USA',
                'website': 'https://www.anacs.com',
                'cert_url_pattern': 'https://portal.anacs.com/Verify/CertVerification.aspx?cert={cert_number}',
                'supported_types': 'coins',
                'is_active': True
            },
            {
                'name': 'Independent Coin Graders',
                'short_name': 'ICG',
                'country': 'USA',
                'website': 'https://www.icgcoin.com',
                'cert_url_pattern': 'https://www.icgcoin.com/load_SNSearch.php?sn={cert_number}',
                'supported_types': 'coins',
                'is_active': True
            },
            {
                'name': 'Certified Acceptance Corporation',
                'short_name': 'CAC',
                'country': 'USA',
                'website': 'https://www.caccoins.com',
                'cert_url_pattern': 'https://www.caccoins.com/verification/{cert_number}',
                'supported_types': 'coins',
                'is_active': True
            }
        ]
        
        # Create companies using ORM
        companies = []
        for company_data in companies_data:
            company = GradingCompany(
                name=company_data['name'],
                short_name=company_data['short_name'],
                country=company_data['country'],
                website=company_data['website'],
                cert_url_pattern=company_data['cert_url_pattern'],
                supported_types=company_data['supported_types'],
                is_active=company_data['is_active']
            )
            session.add(company)
            companies.append(company)
        
        await session.flush()  # This will generate IDs
        
        # Refresh companies to ensure all attributes are loaded
        for company in companies:
            await session.refresh(company)
        
        return companies
    
    def _add_modifiers(self, base_grades):
        """Add modifiers to base grades."""
        result = []
        for g in base_grades:
            result.append(g)
            result.append(f"{g}+")
            result.append(f"{g}★")
            result.append(f"{g}+★")
        return result
    
    def _generate_grades_for_company(self, company_short_name: str) -> list[dict[str, Any]]:
        """Generate grades for a specific company."""
        # Modern coin grades (MS, PR/PF, AU, XF, VF, F, VG, G)
        mint_state_nums = [f"MS {i}" for i in range(60, 71)]
        mint_state_grades = self._add_modifiers(mint_state_nums)

        proof_nums_pf = [f"PF {i}" for i in range(60, 71)]
        ngc_proof_grades = self._add_modifiers(proof_nums_pf)

        proof_nums_pr = [f"PR {i}" for i in range(60, 71)]
        pcgs_proof_grades = self._add_modifiers(proof_nums_pr)

        about_uncirculated_base = ["AU 58", "AU 55", "AU 53", "AU 50"]
        about_uncirculated_grades = self._add_modifiers(about_uncirculated_base)

        extremely_fine_base = ["XF 45", "XF 40"]
        extremely_fine_grades = self._add_modifiers(extremely_fine_base)

        very_fine_base = ["VF 35", "VF 30", "VF 25", "VF 20"]
        very_fine_grades = self._add_modifiers(very_fine_base)

        fine_base = ["F 15", "F 12"]
        fine_grades = self._add_modifiers(fine_base)

        very_good_base = ["VG 10", "VG 8"]
        very_good_grades = self._add_modifiers(very_good_base)

        good_base = ["G 6", "G 4"]
        good_grades = self._add_modifiers(good_base)

        # Details grades
        details_grades = [
            "UNC DETAILS", "VF DETAILS", "AU DETAILS",
            "CLEANING", "CLEANED", "CORROSION", "DAMAGE", "DETAILS",
            "EDGE DAMAGE", "ENVIRONMENTAL DAMAGE", "GRAFFITI", "HARSH CLEANING",
            "HOLED", "HOLE FILLED", "IMPROPERLY CLEANED", "PLUGGED",
            "QUESTIONABLE COLOR", "SCRATCH", "SCRATCHED", "STAINED",
            "TOOLED", "WHIZZED", "ARTIFICIAL TONING", "BENT", "CHOP MARKS",
            "EXCESSIVE CARBON", "EXCESSIVE CORROSION", "FILING", "GROUND",
            "IMPROPERLY STORED", "MOUNTING DAMAGE", "MULTI-STRUCK",
            "NET", "PLANCHET CRACK", "PLANCHET FLAW", "POLISHED",
            "POST-MINT DAMAGE", "PRESS CRACKED", "ROUGH SURFACES",
            "SPOT", "SPOTTED", "SURFACE ENHANCEMENT", "SURFACE HAIRLINES",
            "TEST CUT", "VERDIGRIS",
        ]

        # Special grades
        special_grades = ["GENUINE", "AUTHENTIC"]

        # Ancient grades
        ancient_grades = [
            "Ch XF", "Ch VF", "Ch F", "Ch VG", "Ch G",
            "XF", "VF", "F", "VG", "G", "Fair", "Poor",
            "Superb", "Choice", "Fine", "Very Fine",
        ]

        # Proof designations
        proof_designations = [
            "PROOF", "DEEP CAMEO", "ULTRA CAMEO", "CAMEO",
            "REVERSE PROOF", "DCAM", "UCAM", "CAM",
        ]

        grades = []
        sort_order = 1

        # Add modern grades for PCGS, NGC, ANACS, ICG
        if company_short_name in ["PCGS", "NGC", "ANACS", "ICG"]:
            # Mint State
            for grade in mint_state_grades:
                grades.append({
                    "category": "modern",
                    "value": grade,
                    "sort_order": sort_order,
                })
                sort_order += 1

            # Proof grades - use PF for NGC, PR for PCGS
            proof_grades = ngc_proof_grades if company_short_name == "NGC" else pcgs_proof_grades
            for grade in proof_grades:
                grades.append({
                    "category": "modern",
                    "value": grade,
                    "sort_order": sort_order,
                })
                sort_order += 1

            # Circulated grades
            for grade_list in [about_uncirculated_grades, extremely_fine_grades, 
                              very_fine_grades, fine_grades, very_good_grades, good_grades]:
                for grade in grade_list:
                    grades.append({
                        "category": "modern",
                        "value": grade,
                        "sort_order": sort_order,
                    })
                    sort_order += 1

        # Add details grades for all companies
        for grade in details_grades:
            grades.append({
                "category": "details",
                "value": grade,
                "sort_order": sort_order,
            })
            sort_order += 1

        # Add special grades
        for grade in special_grades:
            grades.append({
                "category": "modern",
                "value": grade,
                "sort_order": sort_order,
            })
            sort_order += 1

        # Add ancient grades for NGC (they grade ancient coins)
        if company_short_name == "NGC":
            for grade in ancient_grades:
                grades.append({
                    "category": "ancient",
                    "value": grade,
                    "sort_order": sort_order,
                })
                sort_order += 1

        # Add proof designations
        for grade in proof_designations:
            grades.append({
                "category": "modern",
                "value": grade,
                "sort_order": sort_order,
            })
            sort_order += 1

        return grades
    
    async def create_grades_for_companies(self, session: AsyncSession, companies):
        """Create grades for all companies using ORM."""
        from models import Grade
        
        all_grades = []
        
        # Extract company data before any potential detachment
        company_data_list = []
        for company in companies:
            company_data_list.append({
                'id': company.id,
                'short_name': company.short_name
            })
        
        for company_data in company_data_list:
            company_grades = self._generate_grades_for_company(company_data['short_name'])
            
            for grade_data in company_grades:
                grade = Grade(
                    company_id=company_data['id'],
                    category=grade_data["category"],
                    value=grade_data["value"],
                    sort_order=grade_data["sort_order"]
                )
                session.add(grade)
                all_grades.append(grade)
        
        await session.flush()
        await session.commit()
        
        return all_grades
    
    async def load_all_grading_data_with_orm(self, session: AsyncSession):
        """Load all grading data using ORM with auto-generated IDs."""
        # First create companies
        companies = await self.create_grading_companies_with_orm(session)
        
        # Then create grades for each company
        grades = await self.create_grades_for_companies(session, companies)
        
        return {
            'companies': companies,
            'grades': grades
        }
