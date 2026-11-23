"""Deterministic qualification and safe output handling; no network dependencies."""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

@dataclass
class Company:
    id: str
    name: str
    industry: str
    employees: int
    region: str
    description: str

def load_companies(path=BASE / 'data' / 'companies.json'):
    return {c['id']: Company(**c) for c in json.loads(Path(path).read_text())}

def qualify(company: Company, icp: dict):
    """Transparent rules baseline; not an LLM prediction."""
    reasons = []
    if company.industry.lower() in [x.lower() for x in icp['industries']]:
        reasons.append('industry_match')
    if icp['min_employees'] <= company.employees <= icp['max_employees']:
        reasons.append('employee_range_match')
    if company.region.lower() in [x.lower() for x in icp['regions']]:
        reasons.append('region_match')
    score = len(reasons) / 3
    return {'score': round(score, 3), 'qualified': len(reasons) == 3, 'reasons': reasons,
            'missing': [x for x in ('industry_match','employee_range_match','region_match') if x not in reasons]}

def research(company: Company):
    """A local, auditable company lookup tool. No web facts invented."""
    return asdict(company)

def generate_recommendation(company: Company, result: dict):
    """Deterministic draft avoids unsupported LLM claims in offline mode."""
    if not result['qualified']:
        return None
    return {'subject': f'Exploring a fit with {company.name}',
            'message': (f'Hello {company.name} team, I noticed your company operates in '
                        f'{company.industry} with approximately {company.employees} employees. '
                        'Would you be open to discussing whether our offering is relevant?'),
            'source_fields': ['name', 'industry', 'employees'], 'requires_approval': True}

def validate_draft(draft):
    if draft is None:
        return True
    return isinstance(draft.get('subject'), str) and isinstance(draft.get('message'), str) and draft.get('requires_approval') is True

def workflow_offline(company_id, icp, companies=None):
    companies = companies or load_companies()
    if company_id not in companies:
        raise KeyError(f'Unknown company: {company_id}')
    company = companies[company_id]
    evidence = research(company)
    decision = qualify(company, icp)
    route = 'approval' if decision['qualified'] else 'rejected'
    draft = generate_recommendation(company, decision)
    assert validate_draft(draft)
    return {'company_id': company_id, 'evidence': evidence, 'qualification': decision,
            'route': route, 'draft': draft, 'approved': False, 'sent': False,
            'mode': 'offline_baseline'}
