import os
import sys
import json
import shutil
import zipfile
import pandas as pd
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# ── helpers ──────────────────────────────────────────────────────────────────

MEDIA = Path(settings.MEDIA_ROOT)
SESSION_KEY = 'idcard_session'

DESIGN_CHOICES = [
    {'id': 'portrait',          'label': 'Portrait – B.A / B.COM',          'courses': ['B.A', 'B.COM'],              'index': 0},
    {'id': 'portrait_bba',      'label': 'Portrait Designed – B.S.(BBA)',   'courses': ['B.S.(BBA)'],                 'index': 1},
    {'id': 'portrait_ma_mcom',  'label': 'Portrait Designed 2 – MA / MCOM', 'courses': ['MA I', 'M COM-I'],           'index': 2},
    {'id': 'landscape',         'label': 'Landscape – Generic',             'courses': [],                            'index': 'landscape'},
    {'id': 'auto',              'label': 'Auto-detect by CourseName',        'courses': [],                            'index': 'auto'},
]

REQUIRED_FIELDS = [
    'RollNumber', 'FirstName', 'Gender', 'Mobile',
    'Address1', 'Semester', 'Subject', 'CourseName',
    'ABC ID', 'PhotoPath', 'BarCodeNumber', 'CourseYear',
]


def get_session_dir(request):
    """Return (and create) a unique upload dir for this browser session."""
    sid = request.session.session_key
    if not sid:
        request.session.create()
        sid = request.session.session_key
    d = MEDIA / 'uploads' / sid
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_state(request):
    return request.session.get(SESSION_KEY, {})


def set_state(request, **kwargs):
    state = request.session.get(SESSION_KEY, {})
    state.update(kwargs)
    request.session[SESSION_KEY] = state
    request.session.modified = True


def load_df(request):
    state = get_state(request)
    csv_path = state.get('csv_path')
    if not csv_path or not Path(csv_path).exists():
        return None
    return pd.read_csv(csv_path, dtype=str).fillna('')


def save_df(request, df):
    state = get_state(request)
    csv_path = state.get('csv_path')
    df.to_csv(csv_path, index=False)


# ── views ────────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'generator/home.html')


def upload(request):
    if request.method == 'GET':
        return render(request, 'generator/upload.html')

    excel_file = request.FILES.get('excel')
    photos_zip = request.FILES.get('photos')

    if not excel_file:
        return render(request, 'generator/upload.html', {'error': 'Please select an Excel file.'})

    session_dir = get_session_dir(request)

    # ── save excel ────────────────────────────────────────────────────────
    excel_path = session_dir / excel_file.name
    with open(excel_path, 'wb') as f:
        for chunk in excel_file.chunks():
            f.write(chunk)

    # ── unzip photos ──────────────────────────────────────────────────────
    photos_dir = None
    if photos_zip:
        zip_path = session_dir / photos_zip.name
        with open(zip_path, 'wb') as f:
            for chunk in photos_zip.chunks():
                f.write(chunk)
        photos_dir = session_dir / 'photos'
        photos_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(photos_dir)

    # ── read excel → CSV ──────────────────────────────────────────────────
    try:
        df = pd.read_excel(excel_path, dtype=str)
        df = df.fillna('')
    except Exception as e:
        return render(request, 'generator/upload.html', {'error': f'Cannot read Excel: {e}'})

    # ── fix PhotoPath to point to extracted photos ────────────────────────
    if photos_dir and 'PhotoPath' in df.columns:
        def resolve_photo(val):
            if not val:
                return val
            name = Path(val).name          # e.g. M601.jpeg
            # search case-insensitively in photos_dir (could be nested)
            for p in photos_dir.rglob('*'):
                if p.name.lower() == name.lower():
                    return str(p)
            # try as-is
            candidate = photos_dir / name
            if candidate.exists():
                return str(candidate)
            return val
        df['PhotoPath'] = df['PhotoPath'].apply(resolve_photo)

    csv_path = session_dir / 'data.csv'
    df.to_csv(csv_path, index=False)

    set_state(request,
              excel_name=excel_file.name,
              csv_path=str(csv_path),
              columns=list(df.columns),
              photos_dir=str(photos_dir) if photos_dir else None,
              pdf_path=None)

    return redirect('map_fields')


def map_fields(request):
    state = get_state(request)
    if not state.get('csv_path'):
        return redirect('upload')

    df = load_df(request)
    excel_columns = list(df.columns)

    if request.method == 'POST':
        mapping = {}
        for req_field in REQUIRED_FIELDS:
            mapped = request.POST.get(f'map_{req_field}', '')
            mapping[req_field] = mapped

        # apply mapping: rename columns and fill missing
        rename = {v: k for k, v in mapping.items() if v and v != '__skip__'}
        df = df.rename(columns=rename)
        for req_field in REQUIRED_FIELDS:
            if req_field not in df.columns:
                df[req_field] = ''

        df.to_csv(state['csv_path'], index=False)
        set_state(request, mapping=mapping, columns=list(df.columns))
        return redirect('preview')

    # auto-detect mapping
    auto_map = {}
    for req in REQUIRED_FIELDS:
        auto_map[req] = req if req in excel_columns else ''

    return render(request, 'generator/map_fields.html', {
        'required_fields': REQUIRED_FIELDS,
        'excel_columns': excel_columns,
        'auto_map': auto_map,
        'excel_name': state.get('excel_name', ''),
        'row_count': len(df),
    })


def preview(request):
    state = get_state(request)
    if not state.get('csv_path'):
        return redirect('upload')

    df = load_df(request)
    if df is None:
        return redirect('upload')

    page = int(request.GET.get('page', 1))
    per_page = 20
    total = len(df)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page

    page_df = df.iloc[start:end]
    rows = page_df.reset_index().to_dict(orient='records')
    # store the absolute row index for edit modal (no underscore prefix — Django templates block those)
    for i, r in enumerate(rows):
        r['row_idx'] = start + i

    columns = [c for c in df.columns if c != 'index']

    # Build a smart page range: always show first, last, and ±2 around current
    def make_page_range(cur, total):
        pages = set()
        pages.update([1, total])
        for i in range(max(1, cur - 2), min(total, cur + 2) + 1):
            pages.add(i)
        result = []
        prev = None
        for p in sorted(pages):
            if prev and p - prev > 1:
                result.append('...')
            result.append(p)
            prev = p
        return result

    return render(request, 'generator/preview.html', {
        'columns': columns,
        'rows': rows,
        'page': page,
        'total_pages': total_pages,
        'total_rows': total,
        'page_range': make_page_range(page, total_pages),
        'excel_name': state.get('excel_name', ''),
    })


def api_row_data(request, idx):
    df = load_df(request)
    if df is None or idx >= len(df):
        return JsonResponse({'error': 'not found'}, status=404)
    row = df.iloc[idx].to_dict()
    return JsonResponse({'row': row, 'idx': idx})


@require_POST
def save_row(request):
    data = json.loads(request.body)
    idx = data.get('idx')
    values = data.get('values', {})

    df = load_df(request)
    if df is None or idx is None or idx >= len(df):
        return JsonResponse({'ok': False, 'error': 'invalid'}, status=400)

    for col, val in values.items():
        if col in df.columns:
            df.at[idx, col] = val

    save_df(request, df)
    return JsonResponse({'ok': True})


def edit_row(request, idx):
    """Not used – editing done inline via modal."""
    return redirect('preview')


def design_select(request):
    state = get_state(request)
    if not state.get('csv_path'):
        return redirect('upload')

    df = load_df(request)

    # detect unique courses
    courses = []
    if 'CourseName' in df.columns:
        courses = sorted(df['CourseName'].dropna().unique().tolist())

    if request.method == 'POST':
        design_id = request.POST.get('design_id', 'auto')
        # Clear any previous pdf_path and mark generation as pending
        set_state(request, design_id=design_id, pdf_path=None, generating=True)
        return redirect('generating')

    return render(request, 'generator/design_select.html', {
        'design_choices': DESIGN_CHOICES,
        'detected_courses': courses,
        'row_count': len(df),
        'excel_name': state.get('excel_name', ''),
    })


def generating(request):
    """Loading page — auto-triggers generation via JS, then polls for completion."""
    state = get_state(request)
    if not state.get('csv_path'):
        return redirect('upload')
    if not state.get('generating'):
        # If not in generating state, go to result or design
        if state.get('pdf_path'):
            return redirect('result')
        return redirect('design_select')
    df = load_df(request)
    row_count = len(df) if df is not None else 0
    return render(request, 'generator/generating.html', {
        'row_count': row_count,
    })


def generate(request):
    state = get_state(request)
    if not state.get('csv_path'):
        return JsonResponse({'ok': False, 'error': 'No session data.'}, status=400)

    df = load_df(request)
    if df is None:
        return JsonResponse({'ok': False, 'error': 'Could not load data.'}, status=400)

    design_id = state.get('design_id', 'auto')
    session_dir = Path(state['csv_path']).parent
    output_pdf = session_dir / 'output.pdf'

    # Switch working directory so Draw.py can find slogo.png, sign.png, etc.
    orig_cwd = os.getcwd()
    os.chdir(str(settings.BASE_DIR))

    # Make sure barcode output dir exists
    barcode_dir = settings.BASE_DIR / 'barcode'
    barcode_dir.mkdir(exist_ok=True)

    try:
        if str(settings.BASE_DIR) not in sys.path:
            sys.path.insert(0, str(settings.BASE_DIR))

        import remaining as pdf_engine
        import importlib
        import Draw
        importlib.reload(Draw)
        importlib.reload(pdf_engine)

        # convert numeric columns back
        for col in ['ABC ID']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).split('.')[0] if x else '')

        design_map = {d['id']: d for d in DESIGN_CHOICES}
        chosen = design_map.get(design_id, design_map['auto'])

        if chosen['index'] == 'auto':
            pdf_engine.create_pdf_4x2(df, str(output_pdf))
        elif chosen['index'] == 'landscape':
            pdf_engine.create_pdf_2x5(df, str(output_pdf))
        else:
            import pdf as pdf_engine2
            importlib.reload(pdf_engine2)
            pdf_engine2.create_pdf_4x2(df, str(output_pdf), index=chosen['index'])

        set_state(request, pdf_path=str(output_pdf), generating=False)
        return JsonResponse({'ok': True, 'redirect': '/result/'})
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        set_state(request, generating=False)
        return JsonResponse({'ok': False, 'error': err})
    finally:
        os.chdir(orig_cwd)


def result(request):
    state = get_state(request)
    pdf_path = state.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        return redirect('upload')

    pdf_size_kb = round(Path(pdf_path).stat().st_size / 1024, 1)
    df = load_df(request)
    return render(request, 'generator/result.html', {
        'pdf_size_kb': pdf_size_kb,
        'row_count': len(df) if df is not None else 0,
        'excel_name': state.get('excel_name', ''),
        'design_id': state.get('design_id', 'auto'),
    })


def download_pdf(request):
    state = get_state(request)
    pdf_path = state.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        return redirect('result')

    response = FileResponse(
        open(pdf_path, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename='id_cards.pdf',
    )
    return response


def view_pdf(request):
    """Serve PDF inline for browser preview (no download dialog)."""
    state = get_state(request)
    pdf_path = state.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        from django.http import Http404
        raise Http404("PDF not found")

    response = FileResponse(
        open(pdf_path, 'rb'),
        content_type='application/pdf',
    )
    response['Content-Disposition'] = 'inline; filename="id_cards.pdf"'
    return response


def clear_cache(request):
    """Delete all uploaded files, sessions, and generated PDFs."""
    uploads = MEDIA / 'uploads'
    if uploads.exists():
        shutil.rmtree(uploads)
    uploads.mkdir(parents=True, exist_ok=True)

    # clear barcode folder
    barcode_dir = settings.BASE_DIR / 'barcode'
    if barcode_dir.exists():
        for f in barcode_dir.iterdir():
            if f.is_file():
                f.unlink()

    # clear this session's state
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]
    request.session.flush()

    return redirect('home')
