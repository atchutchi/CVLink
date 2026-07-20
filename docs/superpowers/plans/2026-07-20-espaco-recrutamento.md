# Espaco de Recrutamento Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private recruiter workspace with shortlist statuses, private tags, saved searches, profile comparison and privacy-safe CSV export.

**Architecture:** Extend the existing `interactions` app because it already owns user-to-profile actions. Preserve existing `Favorite` rows and evolve them into shortlist records, add private `RecruitmentTag` and `SavedSearch`, then expose service-backed views and templates. Keep export and saved-search parameter validation in services so privacy rules are testable without browser-only checks.

**Tech Stack:** Django, SQLite/PostgreSQL-compatible models, Django templates, Django TestCase, Playwright for final browser verification.

## Global Constraints

All user-facing copy must be Portuguese and must not introduce corrupted accent text.

All shortlist, tag, saved-search, comparison and CSV export operations require authentication.

A user can only see and change their own shortlist items, tags and saved searches.

Comparison is limited to 4 profiles.

CSV export must not include email, phone, WhatsApp, private address, private location, or another user's notes/tags.

CSV export must escape values beginning with `=`, `+`, `-` or `@`.

Saved searches must accept only these query keys: `q`, `sector`, `area`, `specialization`, `skill`, `location`, `country`, `availability`, `work_preference`, `experience`, `cv`, `order`.

Do not add automatic email alerts, internal chat, interview scheduling, AI ranking, PDF export or team/company workspaces in this phase.

Each behaviour change must start with a failing automated test.

---

## File Structure

`interactions/models.py`: owns `Favorite`, `RecruitmentTag`, `SavedSearch` and recruitment status choices.

`interactions/forms.py`: owns forms for shortlist metadata and saved-search names.

`interactions/services.py`: owns tag parsing, saved-search parameter validation, CSV building and shortlist comparison selection.

`interactions/views.py`: owns authenticated views for shortlist, saved searches, comparison and export.

`interactions/urls.py`: exposes new routes under the existing `interactions` namespace.

`templates/interactions/favorites.html`: becomes the shortlist workspace.

`templates/interactions/compare.html`: shows side-by-side public profile comparison.

`templates/profiles/search.html`: adds "Guardar pesquisa" and "Adicionar a shortlist" actions.

`templates/profiles/_profile_card.html`: supports optional shortlist action buttons without changing public cards for anonymous users.

`templates/accounts/dashboard.html`: surfaces shortlist and saved searches.

`interactions/tests/test_models.py`, `interactions/tests/test_services.py`, `interactions/tests/test_views.py`: cover the new behaviour.

`static/css/app.css`: adds compact professional styles for shortlist controls, comparison table, saved-search cards and tags.

## Task 1: Data Model for Shortlist, Tags and Saved Searches

**Files:**
- Modify: `interactions/models.py`
- Create: `interactions/migrations/0002_recruitment_workspace.py`
- Test: `interactions/tests/test_models.py`

**Interfaces:**
- Produces: `Favorite.Status` with values `saved`, `to_contact`, `contacted`, `interview`, `offer`, `hired`, `archived`
- Produces: `RecruitmentTag.objects.normalise_name(name: str) -> str`
- Produces: `SavedSearch.allowed_query_params() -> set[str]`

- [ ] **Step 1: Write failing model tests**

Add tests proving:

```python
tag = RecruitmentTag.objects.create(user=self.user, name="  Engenharia Civil  ")
self.assertEqual(tag.name, "Engenharia Civil")
self.assertEqual(tag.normalized_name, "engenharia civil")

favorite = Favorite.objects.create(user=self.user, profile=self.profile, status=Favorite.Status.TO_CONTACT, notes="Boa opção")
favorite.tags.add(tag)
self.assertEqual(favorite.tags.first(), tag)

saved = SavedSearch.objects.create(user=self.user, name="Engenheiros", query_params={"q": "engenheiro", "experience": "5", "unsafe": "x"})
saved.full_clean()
self.assertEqual(saved.query_params, {"q": "engenheiro", "experience": "5"})
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_models -v 2`

Expected: fail because `RecruitmentTag`, `SavedSearch`, `Favorite.Status`, `Favorite.status`, `Favorite.notes` and `Favorite.tags` do not exist yet.

- [ ] **Step 3: Implement minimal models**

Extend `Favorite` with:

```python
class Status(models.TextChoices):
    SAVED = "saved", "Guardado"
    TO_CONTACT = "to_contact", "Para contactar"
    CONTACTED = "contacted", "Contactado"
    INTERVIEW = "interview", "Entrevista"
    OFFER = "offer", "Proposta"
    HIRED = "hired", "Contratado"
    ARCHIVED = "archived", "Arquivado"

status = models.CharField(max_length=24, choices=Status.choices, default=Status.SAVED, db_index=True)
notes = models.TextField(blank=True, max_length=3000)
updated_at = models.DateTimeField(auto_now=True)
tags = models.ManyToManyField("RecruitmentTag", related_name="favorites", blank=True)
```

Add `RecruitmentTag` with `user`, `name`, `normalized_name`, `created_at`, `updated_at`, ordering by name and unique constraint on `user, normalized_name`.

Add `SavedSearch` with `user`, `name`, `query_params`, `created_at`, `updated_at`, ordering by updated date and validation that strips unknown keys and blank values.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_models -v 2`

Expected: pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add interactions/models.py interactions/migrations/0002_recruitment_workspace.py interactions/tests/test_models.py
git commit -m "feat: adicionar modelos de recrutamento"
git push origin main
```

## Task 2: Services for Tags, Saved Searches, Comparison and CSV Export

**Files:**
- Modify: `interactions/services.py`
- Test: `interactions/tests/test_services.py`

**Interfaces:**
- Consumes: `Favorite`, `RecruitmentTag`, `SavedSearch`
- Produces: `sync_favorite_tags(favorite: Favorite, raw_tags: str) -> list[RecruitmentTag]`
- Produces: `clean_saved_search_params(params: Mapping[str, str]) -> dict[str, str]`
- Produces: `get_comparable_favorites(user, profile_ids: list[int]) -> QuerySet[Favorite]`
- Produces: `build_shortlist_csv(user, favorites) -> str`

- [ ] **Step 1: Write failing service tests**

Add tests proving:

```python
favorite = Favorite.objects.create(user=self.user, profile=self.profile)
tags = sync_favorite_tags(favorite, "Civil, urgente, civil")
self.assertEqual([tag.name for tag in tags], ["Civil", "urgente"])
self.assertEqual(favorite.tags.count(), 2)
```

```python
cleaned = clean_saved_search_params({"q": "engenheiro", "unsafe": "x", "experience": "5", "location": ""})
self.assertEqual(cleaned, {"q": "engenheiro", "experience": "5"})
```

```python
owned = get_comparable_favorites(self.user, [self.profile.pk])
self.assertEqual(list(owned), [self.favorite])
self.assertEqual(list(get_comparable_favorites(self.other_user, [self.profile.pk])), [])
```

```python
self.profile.phone = "+245000"
self.profile.whatsapp = "+245111"
self.profile.location = "Rua privada"
self.profile.location_is_public = False
self.profile.save()
self.favorite.notes = "=ligar"
self.favorite.save()
csv_text = build_shortlist_csv(self.user, Favorite.objects.filter(user=self.user))
self.assertIn("'=ligar", csv_text)
self.assertNotIn("+245000", csv_text)
self.assertNotIn("+245111", csv_text)
self.assertNotIn("Rua privada", csv_text)
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_services -v 2`

Expected: fail because the service functions do not exist.

- [ ] **Step 3: Implement minimal services**

Add a private helper:

```python
def escape_csv_value(value):
    text = str(value or "")
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text
```

Build CSV with `csv.DictWriter`, `io.StringIO` and a leading `\ufeff`.

Use `profile.public_payload`, `profile.public_location`, `profile.public_country`, `profile.public_skill_names` and display methods. Never read `profile.phone`, `profile.whatsapp` or `profile.user.email` for CSV.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_services -v 2`

Expected: pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add interactions/services.py interactions/tests/test_services.py
git commit -m "feat: adicionar servicos de shortlist"
git push origin main
```

## Task 3: Authenticated Views and Routes

**Files:**
- Modify: `interactions/forms.py`
- Modify: `interactions/views.py`
- Modify: `interactions/urls.py`
- Test: `interactions/tests/test_views.py`

**Interfaces:**
- Consumes: services from Task 2
- Produces route names: `interactions:favorites`, `interactions:favorite-update`, `interactions:saved-search-create`, `interactions:saved-search-delete`, `interactions:saved-search-run`, `interactions:compare`, `interactions:shortlist-export`

- [ ] **Step 1: Write failing view tests**

Add tests proving:

```python
response = self.client.post(reverse("interactions:favorite-update", args=(self.favorite.pk,)), {"status": "interview", "notes": "Boa entrevista", "tags": "civil, senior"})
self.assertRedirects(response, reverse("interactions:favorites"))
self.favorite.refresh_from_db()
self.assertEqual(self.favorite.status, Favorite.Status.INTERVIEW)
self.assertEqual(self.favorite.notes, "Boa entrevista")
```

```python
response = self.client.post(reverse("interactions:saved-search-create"), {"name": "Engenharia", "q": "engenheiro", "experience": "5", "unsafe": "x"})
self.assertRedirects(response, reverse("search") + "?q=engenheiro&experience=5")
self.assertEqual(SavedSearch.objects.get(user=self.user).query_params, {"q": "engenheiro", "experience": "5"})
```

```python
response = self.client.get(reverse("interactions:compare"), {"profiles": str(self.profile.pk)})
self.assertContains(response, self.profile.public_display_name)
self.assertNotContains(response, self.profile.phone)
```

```python
response = self.client.get(reverse("interactions:shortlist-export"))
self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
self.assertNotContains(response, self.profile.user.email)
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`

Expected: fail because routes and views do not exist.

- [ ] **Step 3: Implement forms, views and URLs**

Add:

```python
class FavoriteUpdateForm(forms.ModelForm):
    tags = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Favorite
        fields = ("status", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}
```

Add:

```python
class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ("name",)
```

Implement authenticated views using `get_object_or_404(..., user=request.user)`. For CSV return `HttpResponse(csv_text, content_type="text/csv; charset=utf-8")` with `Content-Disposition`.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`

Expected: pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add interactions/forms.py interactions/views.py interactions/urls.py interactions/tests/test_views.py
git commit -m "feat: adicionar vistas de recrutamento"
git push origin main
```

## Task 4: Recruiter UI

**Files:**
- Modify: `templates/interactions/favorites.html`
- Create: `templates/interactions/compare.html`
- Modify: `templates/profiles/search.html`
- Modify: `templates/profiles/_profile_card.html`
- Modify: `templates/accounts/dashboard.html`
- Modify: `static/css/app.css`
- Test: `interactions/tests/test_views.py`

**Interfaces:**
- Consumes: route names from Task 3
- Produces visible UI for shortlist, saved searches, compare and export

- [ ] **Step 1: Write failing template tests**

Add tests proving:

```python
response = self.client.get(reverse("interactions:favorites"))
self.assertContains(response, "Shortlist")
self.assertContains(response, "Estado do processo")
self.assertContains(response, "Exportar CSV")
self.assertContains(response, "Comparar seleccionados")
```

```python
response = self.client.get(reverse("search"), {"q": "engenheiro", "experience": "5"})
self.assertContains(response, "Guardar pesquisa")
self.assertContains(response, "Adicionar a shortlist")
```

```python
response = self.client.get(reverse("accounts:dashboard"))
self.assertContains(response, "Pesquisas guardadas")
self.assertContains(response, "Shortlist")
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`

Expected: fail because the copy and UI elements are not present yet.

- [ ] **Step 3: Implement templates and styles**

Update shortlist page to show filters, editable status, private notes, private tags, checkboxes for compare, export action and profile link.

Update search page to show a save-search form for authenticated users and card-level shortlist action. Anonymous users should see existing public result cards without private controls.

Update dashboard with sections for recent saved searches and shortlist count.

Add compact CSS classes: `.shortlist-toolbar`, `.shortlist-item`, `.recruitment-status`, `.saved-search-list`, `.compare-table`, `.private-tag`.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `.venv\Scripts\python.exe manage.py test interactions.tests.test_views -v 2`

Expected: pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add templates/interactions/favorites.html templates/interactions/compare.html templates/profiles/search.html templates/profiles/_profile_card.html templates/accounts/dashboard.html static/css/app.css interactions/tests/test_views.py
git commit -m "feat: melhorar interface de recrutamento"
git push origin main
```

## Task 5: Full Verification and Browser QA

**Files:**
- Modify only if tests expose defects in files already touched by Tasks 1 to 4.

**Interfaces:**
- Consumes: all prior tasks
- Produces: verified local site running at `http://127.0.0.1:8000/`

- [ ] **Step 1: Run full automated suite**

Run: `.venv\Scripts\python.exe manage.py test -v 2`

Expected: all tests pass.

- [ ] **Step 2: Apply migrations locally**

Run: `.venv\Scripts\python.exe manage.py migrate`

Expected: migrations apply without errors.

- [ ] **Step 3: Run Playwright checks**

Use Playwright to verify:

```text
Login
Pesquisar por engenheiro com experience=5
Guardar pesquisa
Adicionar perfil a shortlist
Editar estado, notas e etiquetas
Comparar um perfil
Exportar CSV
Voltar ao painel
```

Expected: no server error, no corrupted accent text visible, private candidate contacts absent from comparison and CSV.

- [ ] **Step 4: Commit any verification fixes**

Only if fixes are needed:

```bash
git add <changed-files>
git commit -m "fix: estabilizar recrutamento"
git push origin main
```

- [ ] **Step 5: Final status**

Confirm:

```bash
git status --short
git log --oneline -5
```

Expected: clean worktree and latest commits pushed to `origin/main`.

