# Production Grading Data Generator

Generates SQL file with grading companies and their grade scales for production deployment.

## Usage

```bash
# Generate data for all companies (PCGS, NGC, ANACS, ICG, CAC)
python3 generate_production_grading_data.py

# Generate data for specific companies only
python3 generate_production_grading_data.py PCGS NGC
```

## Output

- **File**: `prepared_sql/production_grading_data.sql`
- **Content**: INSERT statements for companies and grades with UUIDs
- **Statistics**: ~900 grades across 5 major companies

## Deployment

```bash
# Apply to production database
psql $DATABASE_URL < prepared_sql/production_grading_data.sql
```

## Docker Execution

```bash
# Run from project root
docker compose --profile tools run --rm numismatist_dev_tools 
  sh -c "cd /app/src/utils/data_preparation && python3 generate_production_grading_data.py"
```

## Features

- ✅ Generates UUIDs for companies using `str(uuid4())`
- ✅ Creates proper foreign key relationships between companies and grades
- ✅ No database connection required
- ✅ Self-contained SQL generation
- ✅ Supports selective company generation

## Grade Categories

### Modern Grades
- **Mint State (MS)**: MS 60-70 with modifiers (+, ★, +★)
- **Proof (PR/PF)**: PR/PF 60-70 with modifiers (NGC uses PF, others use PR)
- **Circulated**: AU 50-58, XF 40-45, VF 20-35, F 12-15, VG 8-10, G 4-6

### Details Grades
- Cleaning, damage, environmental issues
- Post-mint damage designations
- Surface problems and alterations

### Ancient Grades
- Traditional ancient coin grading (NGC only)
- Choice designations (Ch XF, Ch VF, etc.)

### Special Designations
- Proof types (Deep Cameo, Ultra Cameo, etc.)
- Authentication grades (Genuine, Authentic)

## File Structure

```
data_preparation/
├── README.md                           # This file
├── generate_production_grading_data.py # Unified generator
└── prepared_sql/                       # Generated SQL files
    ├── .gitignore                      # Ignore generated files
    └── production_grading_data.sql     # Complete data file
```

## Notes

- All UUIDs are generated using `str(uuid4())` following the `UuidPkMixin` pattern
- No hardcoded UUIDs - each run generates fresh UUIDs
- Foreign key relationships between companies and grades are maintained
- Generated files are excluded from git via `.gitignore`
- No database connection required for data generation
