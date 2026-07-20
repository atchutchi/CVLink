status: DONE

commits created:
- feat: melhorar interface de recrutamento

RED test command and observed failure:
- `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`
- Failed as expected with 3 missing UI behaviours: `Guardar pesquisa`, `Pesquisas guardadas` and `Shortlist` workspace text.

GREEN test command and result:
- `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`
- Result: 26 tests passed, exit code 0.

text encoding scan result:
- `Select-String` on the five touched templates found no occurrences of `Ãƒ`, `Ã‚` or `??`.

self-review notes:
- The shortlist supports status and tag filters, CSV export, comparison selection, private notes, tags, process status and removal.
- Search actions are visible only to authenticated users. The comparison table exposes only approved public profile data and hides private location.
- The layout has horizontal overflow protection for the comparison table and switches shortlist rows to one column on smaller screens.

concerns:
- None.
