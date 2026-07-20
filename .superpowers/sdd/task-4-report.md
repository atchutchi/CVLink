status: DONE

commits created:
- feat: melhorar interface de recrutamento
- fix: proteger comparacao publica
- test: cobrir redirect seguro de pesquisa

RED test command and observed failure:
- `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`
- Initially failed as expected with 3 missing UI behaviours: `Guardar pesquisa`, `Pesquisas guardadas` and `Shortlist` workspace text.
- Regression correction failed as expected when comparison exposed current recruitment data and saved-search deletion redirected to shortlist.

GREEN test command and result:
- `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`
- Result: 29 tests passed, exit code 0.

text encoding scan result:
- `Select-String` on the five touched templates found no occurrences of `Ãƒ`, `Ã‚` or `??`.

self-review notes:
- The shortlist supports status and tag filters, CSV export, comparison selection, private notes, tags, process status and removal.
- Search actions are visible only to authenticated users. The comparison table consumes the public snapshot for recruitment details and hides private location.
- Deleting a saved search from the dashboard returns there only when the requested destination is local and safe.
- External `next` destinations fall back to the shortlist and are covered by regression testing.
- The layout has horizontal overflow protection for the comparison table and switches shortlist rows to one column on smaller screens.

concerns:
- None.
