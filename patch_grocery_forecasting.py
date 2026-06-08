from pathlib import Path

path = Path(r'c:/Users/lenovo/Desktop/BI Project/bi/AI/grocery_forecasting.ipynb')
text = path.read_text(encoding='utf-8')
old1 = '    "df = add_covid_flags(df)\\n",\n    "df = add_time_features(df)\\n",\n    "\\n",\n    "print(\\\"✅ Features créées :\\\")\\n",\n'
new1 = '    "df = add_covid_flags(df)\\n",\n    "df = add_time_features(df)\\n",\n    "\\n",\n    "# Garder uniquement les colonnes utiles pour le modèle\\n",\n    "df = df[[\\\"revenue\\\", \\\"trend\\\", \\\"month_sin\\\", \\\"month_cos\\\", \\\"is_december\\\", \\\"is_summer\\\", \\\"covid_flag\\\"]]\\n",\n    "\\n",\n    "print(\\\"✅ Features créées :\\\")\\n",\n'
old2 = '    "FEATURES = [\\n",\n    "    \\\"trend\\\", \\\"year_norm\\\",\\n",\n    "    \\\"month_sin\\\", \\\"month_cos\\\",\\n",\n    "    \\\"is_december\\\", \\\"is_summer\\\", \\\"is_q4\\\", \\\"is_q1\\\",\\n",\n    "    \\\"covid_severe\\\", \\\"covid_moderate\\\",\\n",\n    "    \\\"lag_1\\\", \\\"lag_12\\\", \\\"roll_3m\\\", \\\"roll_6m\\\"\\n",\n    \"]\\n",\n'
new2 = '    "FEATURES = [\\n",\n    "    \\\"trend\\\",\\n",\n    "    \\\"month_sin\\\", \\\"month_cos\\\",\\n",\n    "    \\\"is_december\\\", \\\"is_summer\\\",\\n",\n    "    \\\"covid_flag\\\",\\n",\n    \"]\\n",\n'

if old1 not in text:
    raise SystemExit('old1 not found')
text = text.replace(old1, new1, 1)
if old2 not in text:
    raise SystemExit('old2 not found')
text = text.replace(old2, new2, 1)
path.write_text(text, encoding='utf-8')
print('patched')
