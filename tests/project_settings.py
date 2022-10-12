settings = {
    'general': {
        'verbose': True,
        'seed': 43,
        'conserve_memory': False,
        'parallelize': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'cool_project': {
        'cool_project_structure': 'pipeline',
        'cool_project_managers': ['reviewer', 'parser', 'munger']},
    'reviewer': {
        'reviewer_design': 'laborer',
        'reviewer_techniques': ['scan', 'view'],
        'scan_techniques': ['spy', 'look', 'eye'],
        'look_techniques': ['peer', 'see']},
    'parser': {
        'parser_design': 'contest',
        'parser_steps': ['divide', 'extract'],
        'divide_techniques': ['slice', 'dice'],
        'extract_techniques': ['harvest', 'process', 'something'],
        'random_thing': True},
    'munger': {
        'munger_design': 'survey',
        'munger_steps': ['search', 'destroy'],
        'search_techniques': ['find', 'locate'],
        'destroy_techniques': ['explode', 'dynamite']},
    'divide_parameters': {'replace_strings': True}}
