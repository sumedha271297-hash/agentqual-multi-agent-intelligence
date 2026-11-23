"""Bounded, auditable local research tool; external data providers can replace this adapter."""
from dataclasses import asdict
from time import perf_counter, sleep
from app.core import load_companies

class ToolFailure(RuntimeError):
    pass

def company_lookup(company_id: str, *, attempts: int = 3, backoff: float = 0.01, provider=None):
    """Retry transient provider failures; never retry a missing company."""
    if attempts < 1 or attempts > 5:
        raise ValueError('attempts must be between 1 and 5')
    provider = provider or (lambda key: asdict(load_companies()[key]))
    started = perf_counter()
    for attempt in range(attempts):
        try:
            result = provider(company_id)
            required = {'id', 'name', 'industry', 'employees', 'region', 'description'}
            if not isinstance(result, dict) or not required.issubset(result):
                raise ToolFailure('Invalid provider response')
            return {'data': result, 'metadata': {'tool': 'company_lookup', 'attempts': attempt + 1,
                     'elapsed_ms': round((perf_counter() - started) * 1000, 3)}}
        except KeyError:
            raise
        except (TimeoutError, ConnectionError, ToolFailure) as exc:
            if attempt == attempts - 1:
                raise ToolFailure(f'Company lookup failed after {attempts} attempts') from exc
            sleep(backoff * (2 ** attempt))
