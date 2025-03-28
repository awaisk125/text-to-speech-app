from flask import Flask, request, abort, jsonify, send_file, render_template
import asyncio
import edge_tts
import os
import uuid

app = Flask(__name__)


# Security Configuration
ALLOWED_DOMAIN = "https://voicenova.site"  # Your website domain

@app.before_request
def check_referer():
    """Block requests not coming from your website"""
    # Skip security checks for static files (if any)
    if request.path.startswith('/static/'):
        return
        
    referer = request.headers.get('Referer')
    if not referer or not referer.startswith(ALLOWED_DOMAIN):
        abort(403, "Access denied: Please use this app through voicenova.site")

@app.after_request
def add_csp(response):
    """Prevent embedding on other sites"""
    response.headers['Content-Security-Policy'] = f"frame-ancestors {ALLOWED_DOMAIN};"
    return response



# Store the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Language and voice mapping (example data)
LANGUAGE_NAMES = {
        "ps-AF": "Pashto-Afghanistan",
        "fa-AF": "Persian-Afghanistan",
        "uz-AF": "Uzbek-Afghanistan",
        "sv-AX": "Swedish-Åland Islands",
        "sq-AL": "Albanian-Albania",
        "en-AL": "English-Albania",
        "ar-DZ": "Arabic-Algeria",
        "fr-DZ": "French-Algeria",
        "kab-DZ": "Kabyle-Algeria",
        "en-AS": "English-American Samoa",
        "ca-AD": "Catalan-Andorra",
        "en-AD": "English-Andorra",
        "ln-AO": "Lingala-Angola",
        "pt-AO": "Portuguese-Angola",
        "en-AI": "English-Anguilla",
        "es-AI": "Spanish-Anguilla",
        "en-AG": "English-Antigua & Barbuda",
        "es-AG": "Spanish-Antigua & Barbuda",
        "en-AR": "English-Argentina",
        "es-AR": "Spanish-Argentina",
        "hy-AM": "Armenian-Armenia",
        "nl-AW": "Dutch-Aruba",
        "es-AW": "Spanish-Aruba",
        "en-AU": "English-Australia",
        "en-AT": "English-Austria",
        "de-AT": "German-Austria",
        "az-AZ": "Azerbaijani-Azerbaijan",
        "en-BS": "English-Bahamas",
        "es-BS": "Spanish-Bahamas",
        "ar-BH": "Arabic-Bahrain",
        "bn-BD": "Bangla-Bangladesh",
        "ccp-BD": "Chakma-Bangladesh",
        "en-BD": "English-Bangladesh",
        "en-BB": "English-Barbados",
        "es-BB": "Spanish-Barbados",
        "be-BY": "Belarusian-Belarus",
        "ru-BY": "Russian-Belarus",
        "nl-BE": "Dutch-Belgium",
        "en-BE": "English-Belgium",
        "fr-BE": "French-Belgium",
        "de-BE": "German-Belgium",
        "wa-BE": "Walloon-Belgium",
        "en-BZ": "English-Belize",
        "es-BZ": "Spanish-Belize",
        "fr-BJ": "French-Benin",
        "yo-BJ": "Yoruba-Benin",
        "en-BM": "English-Bermuda",
        "es-BM": "Spanish-Bermuda",
        "dz-BT": "Dzongkha-Bhutan",
        "qu-BO": "Quechua-Bolivia",
        "es-BO": "Spanish-Bolivia",
        "bs-BA": "Bosnian-Bosnia & Herzegovina",
        "hr-BA": "Croatian-Bosnia & Herzegovina",
        "en-BA": "English-Bosnia & Herzegovina",
        "sr-BA": "Serbian-Bosnia & Herzegovina",
        "en-BW": "English-Botswana",
        "tn-BW": "Tswana-Botswana",
        "en-BR": "English-Brazil",
        "pt-BR": "Portuguese-Brazil",
        "es-BR": "Spanish-Brazil",
        "en-IO": "English-British Indian Ocean Territory",
        "en-VG": "English-British Virgin Islands",
        "es-VG": "Spanish-British Virgin Islands",
        "ms-BN": "Malay-Brunei",
        "bg-BG": "Bulgarian-Bulgaria",
        "en-BG": "English-Bulgaria",
        "fr-BF": "French-Burkina Faso",
        "ff-BF": "Fulah-Burkina Faso",
        "en-BI": "English-Burundi",
        "fr-BI": "French-Burundi",
        "rn-BI": "Rundi-Burundi",
        "km-KH": "Khmer-Cambodia",
        "agq-CM": "Aghem-Cameroon",
        "ksf-CM": "Bafia-Cameroon",
        "bas-CM": "Basaa-Cameroon",
        "dua-CM": "Duala-Cameroon",
        "en-CM": "English-Cameroon",
        "ewo-CM": "Ewondo-Cameroon",
        "fr-CM": "French-Cameroon",
        "ff-CM": "Fulah-Cameroon",
        "kkj-CM": "Kako-Cameroon",
        "nmg-CM": "Kwasio-Cameroon",
        "mgo-CM": "Meta-Cameroon",
        "mua-CM": "Mundang-Cameroon",
        "nnh-CM": "Ngiemboon-Cameroon",
        "jgo-CM": "Ngomba-Cameroon",
        "yav-CM": "Yangben-Cameroon",
        "en-CA": "English-Canada",
        "fr-CA": "French-Canada",
        "iu-CA": "Inuktitut-Canada",
        "moh-CA": "Mohawk-Canada",
        "es-CA": "Spanish-Canada",
        "es-IC": "Spanish-Canary Islands",
        "kea-CV": "Kabuverdianu-Cape Verde",
        "pt-CV": "Portuguese-Cape Verde",
        "nl-BQ": "Dutch-Caribbean Netherlands",
        "es-BQ": "Spanish-Caribbean Netherlands",
        "en-KY": "English-Cayman Islands",
        "es-KY": "Spanish-Cayman Islands",
        "fr-CF": "French-Central African Republic",
        "ln-CF": "Lingala-Central African Republic",
        "sg-CF": "Sango-Central African Republic",
        "es-EA": "Spanish-Ceuta & Melilla",
        "ar-TD": "Arabic-Chad",
        "fr-TD": "French-Chad",
        "en-CL": "English-Chile",
        "arn-CL": "Mapuche-Chile",
        "es-CL": "Spanish-Chile",
        "yue-CN": "Cantonese-China mainland",
        "zh-CN": "Chinese-China mainland",
        "en-CN": "English-China mainland",
        "ii-CN": "Sichuan Yi-China mainland",
        "bo-CN": "Tibetan-China mainland",
        "ug-CN": "Uyghur-China mainland",
        "en-CX": "English-Christmas Island",
        "en-CC": "English-Cocos (Keeling) Islands",
        "en-CO": "English-Colombia",
        "es-CO": "Spanish-Colombia",
        "ar-KM": "Arabic-Comoros",
        "fr-KM": "French-Comoros",
        "fr-CG": "French-Congo - Brazzaville",
        "ln-CG": "Lingala-Congo - Brazzaville",
        "fr-CD": "French-Congo - Kinshasa",
        "ln-CD": "Lingala-Congo - Kinshasa",
        "lu-CD": "Luba-Katanga-Congo - Kinshasa",
        "sw-CD": "Swahili-Congo - Kinshasa",
        "en-CK": "English-Cook Islands",
        "es-CR": "Spanish-Costa Rica",
        "fr-CI": "French-Côte d’Ivoire",
        "hr-HR": "Croatian-Croatia",
        "en-HR": "English-Croatia",
        "es-CU": "Spanish-Cuba",
        "nl-CW": "Dutch-Curaçao",
        "es-CW": "Spanish-Curaçao",
        "en-CY": "English-Cyprus",
        "el-CY": "Greek-Cyprus",
        "tr-CY": "Turkish-Cyprus",
        "cs-CZ": "Czech-Czechia",
        "en-CZ": "English-Czechia",
        "da-DK": "Danish-Denmark",
        "en-DK": "English-Denmark",
        "fo-DK": "Faroese-Denmark",
        "en-DG": "English-Diego Garcia",
        "ar-DJ": "Arabic-Djibouti",
        "fr-DJ": "French-Djibouti",
        "so-DJ": "Somali-Djibouti",
        "en-DM": "English-Dominica",
        "es-DM": "Spanish-Dominica",
        "es-DO": "Spanish-Dominican Republic",
        "qu-EC": "Quechua-Ecuador",
        "es-EC": "Spanish-Ecuador",
        "ar-EG": "Arabic-Egypt",
        "es-SV": "Spanish-El Salvador",
        "fr-GQ": "French-Equatorial Guinea",
        "pt-GQ": "Portuguese-Equatorial Guinea",
        "es-GQ": "Spanish-Equatorial Guinea",
        "ar-ER": "Arabic-Eritrea",
        "byn-ER": "Blin-Eritrea",
        "en-ER": "English-Eritrea",
        "gez-ER": "Geez-Eritrea",
        "tig-ER": "Tigre-Eritrea",
        "ti-ER": "Tigrinya-Eritrea",
        "en-EE": "English-Estonia",
        "et-EE": "Estonian-Estonia",
        "en-SZ": "English-Eswatini",
        "ss-SZ": "Swati-Eswatini",
        "am-ET": "Amharic-Ethiopia",
        "gez-ET": "Geez-Ethiopia",
        "om-ET": "Oromo-Ethiopia",
        "so-ET": "Somali-Ethiopia",
        "ti-ET": "Tigrinya-Ethiopia",
        "wal-ET": "Wolaytta-Ethiopia",
        "en-150": "English-Europe",
        "en-FK": "English-Falkland Islands",
        "es-FK": "Spanish-Falkland Islands",
        "fo-FO": "Faroese-Faroe Islands",
        "en-FJ": "English-Fiji",
        "en-FI": "English-Finland",
        "fi-FI": "Finnish-Finland",
        "smn-FI": "Inari Sami-Finland",
        "se-FI": "Northern Sami-Finland",
        "sv-FI": "Swedish-Finland",
        "br-FR": "Breton-France",
        "ca-FR": "Catalan-France",
        "co-FR": "Corsican-France",
        "en-FR": "English-France",
        "fr-FR": "French-France",
        "oc-FR": "Occitan-France",
        "pt-FR": "Portuguese-France",
        "gsw-FR": "Swiss German-France",
        "fr-GF": "French-French Guiana",
        "es-GF": "Spanish-French Guiana",
        "fr-PF": "French-French Polynesia",
        "fr-GA": "French-Gabon",
        "en-GM": "English-Gambia",
        "ff-GM": "Fulah-Gambia",
        "ka-GE": "Georgian-Georgia",
        "os-GE": "Ossetic-Georgia",
        "ksh-DE": "Colognian-Germany",
        "en-DE": "English-Germany",
        "de-DE": "German-Germany",
        "nds-DE": "Low German-Germany",
        "dsb-DE": "Lower Sorbian-Germany",
        "hsb-DE": "Upper Sorbian-Germany",
        "ak-GH": "Akan-Ghana",
        "en-GH": "English-Ghana",
        "ee-GH": "Ewe-Ghana",
        "ff-GH": "Fulah-Ghana",
        "gaa-GH": "Ga-Ghana",
        "ha-GH": "Hausa-Ghana",
        "en-GI": "English-Gibraltar",
        "en-GR": "English-Greece",
        "el-GR": "Greek-Greece",
        "da-GL": "Danish-Greenland",
        "kl-GL": "Kalaallisut-Greenland",
        "es-GL": "Spanish-Greenland",
        "en-GD": "English-Grenada",
        "es-GD": "Spanish-Grenada",
        "fr-GP": "French-Guadeloupe",
        "es-GP": "Spanish-Guadeloupe",
        "en-GU": "English-Guam",
        "es-GT": "Spanish-Guatemala",
        "en-GG": "English-Guernsey",
        "ff-GW": "Fulah-Guinea-Bissau",
        "pt-GW": "Portuguese-Guinea-Bissau",
        "fr-GN": "French-Guinea",
        "ff-GN": "Fulah-Guinea",
        "kpe-GN": "Kpelle-Guinea",
        "nqo-GN": "N’Ko-Guinea",
        "en-GY": "English-Guyana",
        "es-GY": "Spanish-Guyana",
        "fr-HT": "French-Haiti",
        "es-HT": "Spanish-Haiti",
        "es-HN": "Spanish-Honduras",
        "yue-HK": "Cantonese-Hong Kong",
        "zh-HK": "Chinese-Hong Kong",
        "en-HK": "English-Hong Kong",
        "en-HU": "English-Hungary",
        "hu-HU": "Hungarian-Hungary",
        "en-IS": "English-Iceland",
        "is-IS": "Icelandic-Iceland",
        "as-IN": "Assamese-India",
        "bn-IN": "Bangla-India",
        "brx-IN": "Bodo-India",
        "ccp-IN": "Chakma-India",
        "en-IN": "English-India",
        "gu-IN": "Gujarati-India",
        "hi-IN": "Hindi-India",
        "kn-IN": "Kannada-India",
        "ks-IN": "Kashmiri-India",
        "kok-IN": "Konkani-India",
        "ml-IN": "Malayalam-India",
        "mni-IN": "Manipuri-India",
        "mr-IN": "Marathi-India",
        "ne-IN": "Nepali-India",
        "or-IN": "Odia-India",
        "pa-IN": "Punjabi-India",
        "sa-IN": "Sanskrit-India",
        "sat-IN": "Santali-India",
        "ta-IN": "Tamil-India",
        "te-IN": "Telugu-India",
        "bo-IN": "Tibetan-India",
        "ur-IN": "Urdu-India",
        "en-ID": "English-Indonesia",
        "id-ID": "Indonesian-Indonesia",
        "jv-ID": "Javanese-Indonesia",
        "ckb-IR": "Kurdish, Sorani-Iran",
        "mzn-IR": "Mazanderani-Iran",
        "lrc-IR": "Northern Luri-Iran",
        "fa-IR": "Persian-Iran",
        "ar-IQ": "Arabic-Iraq",
        "ckb-IQ": "Kurdish, Sorani-Iraq",
        "lrc-IQ": "Northern Luri-Iraq",
        "syr-IQ": "Syriac-Iraq",
        "en-IE": "English-Ireland",
        "ga-IE": "Irish-Ireland",
        "en-IM": "English-Isle of Man",
        "gv-IM": "Manx-Isle of Man",
        "ar-IL": "Arabic-Israel",
        "en-IL": "English-Israel",
        "he-IL": "Hebrew-Israel",
        "ca-IT": "Catalan-Italy",
        "en-IT": "English-Italy",
        "fur-IT": "Friulian-Italy",
        "de-IT": "German-Italy",
        "it-IT": "Italian-Italy",
        "sc-IT": "Sardinian-Italy",
        "scn-IT": "Sicilian-Italy",
        "en-JM": "English-Jamaica",
        "en-JP": "English-Japan",
        "ja-JP": "Japanese-Japan",
        "en-JE": "English-Jersey",
        "ar-JO": "Arabic-Jordan",
        "kk-KZ": "Kazakh-Kazakhstan",
        "ru-KZ": "Russian-Kazakhstan",
        "ebu-KE": "Embu-Kenya",
        "en-KE": "English-Kenya",
        "guz-KE": "Gusii-Kenya",
        "kln-KE": "Kalenjin-Kenya",
        "kam-KE": "Kamba-Kenya",
        "ki-KE": "Kikuyu-Kenya",
        "luo-KE": "Luo-Kenya",
        "luy-KE": "Luyia-Kenya",
        "mas-KE": "Masai-Kenya",
        "mer-KE": "Meru-Kenya",
        "om-KE": "Oromo-Kenya",
        "saq-KE": "Samburu-Kenya",
        "so-KE": "Somali-Kenya",
        "sw-KE": "Swahili-Kenya",
        "dav-KE": "Taita-Kenya",
        "teo-KE": "Teso-Kenya",
        "en-KI": "English-Kiribati",
        "sq-XK": "Albanian-Kosovo",
        "sr-XK": "Serbian-Kosovo",
        "ar-KW": "Arabic-Kuwait",
        "ky-KG": "Kyrgyz-Kyrgyzstan",
		"lo-LA": "Lao-Laos",
		"es-419": "Spanish-Latin America",
		"en-LV": "English-Latvia",
		"lv-LV": "Latvian-Latvia",
		"ar-LB": "Arabic-Lebanon",
		"en-LS": "English-Lesotho",
		"st-LS": "Southern Sotho-Lesotho",
		"en-LR": "English-Liberia",
		"ff-LR": "Fulah-Liberia",
		"kpe-LR": "Kpelle-Liberia",
		"vai-LR": "Vai-Liberia",
		"ar-LY": "Arabic-Libya",
		"de-LI": "German-Liechtenstein",
		"gsw-LI": "Swiss German-Liechtenstein",
		"en-LT": "English-Lithuania",
		"lt-LT": "Lithuanian-Lithuania",
		"en-LU": "English-Luxembourg",
		"fr-LU": "French-Luxembourg",
		"de-LU": "German-Luxembourg",
		"lb-LU": "Luxembourgish-Luxembourg",
		"pt-LU": "Portuguese-Luxembourg",
		"zh-MO": "Chinese-Macao",
		"en-MO": "English-Macao",
		"pt-MO": "Portuguese-Macao",
		"en-MG": "English-Madagascar",
		"fr-MG": "French-Madagascar",
		"mg-MG": "Malagasy-Madagascar",
		"en-MW": "English-Malawi",
		"ny-MW": "Nyanja-Malawi",
		"en-MY": "English-Malaysia",
		"ms-MY": "Malay-Malaysia",
		"ta-MY": "Tamil-Malaysia",
		"dv-MV": "Dhivehi-Maldives",
		"en-MV": "English-Maldives",
		"bm-ML": "Bambara-Mali",
		"fr-ML": "French-Mali",
		"khq-ML": "Koyra Chiini-Mali",
		"ses-ML": "Koyraboro Senni-Mali",
		"en-MT": "English-Malta",
		"mt-MT": "Maltese-Malta",
		"en-MH": "English-Marshall Islands",
		"fr-MQ": "French-Martinique",
		"es-MQ": "Spanish-Martinique",
		"ar-MR": "Arabic-Mauritania",
		"fr-MR": "French-Mauritania",
		"ff-MR": "Fulah-Mauritania",
		"en-MU": "English-Mauritius",
		"fr-MU": "French-Mauritius",
		"mfe-MU": "Morisyen-Mauritius",
		"fr-YT": "French-Mayotte",
		"en-MX": "English-Mexico",
		"es-MX": "Spanish-Mexico",
		"en-FM": "English-Micronesia",
		"ro-MD": "Romanian-Moldova",
		"ru-MD": "Russian-Moldova",
		"fr-MC": "French-Monaco",
		"mn-MN": "Mongolian-Mongolia",
		"en-ME": "English-Montenegro",
		"sr-ME": "Serbian-Montenegro",
		"en-MS": "English-Montserrat",
		"es-MS": "Spanish-Montserrat",
		"ar-MA": "Arabic-Morocco",
		"tzm-MA": "Central Atlas Tamazight-Morocco",
		"fr-MA": "French-Morocco",
		"zgh-MA": "Standard Moroccan Tamazight-Morocco",
		"shi-MA": "Tachelhit-Morocco",
		"mgh-MZ": "Makhuwa-Meetto-Mozambique",
		"pt-MZ": "Portuguese-Mozambique",
		"seh-MZ": "Sena-Mozambique",
		"my-MM": "Burmese-Myanmar (Burma)",
		"en-MM": "English-Myanmar (Burma)",
		"af-NA": "Afrikaans-Namibia",
		"en-NA": "English-Namibia",
		"naq-NA": "Nama-Namibia",
		"en-NR": "English-Nauru",
		"ne-NP": "Nepali-Nepal",
		"nl-NL": "Dutch-Netherlands",
		"en-NL": "English-Netherlands",
		"nds-NL": "Low German-Netherlands",
		"fy-NL": "Western Frisian-Netherlands",
		"fr-NC": "French-New Caledonia",
		"en-NZ": "English-New Zealand",
		"mi-NZ": "Maori-New Zealand",
		"es-NI": "Spanish-Nicaragua",
		"fr-NE": "French-Niger",
		"ff-NE": "Fulah-Niger",
		"ha-NE": "Hausa-Niger",
		"twq-NE": "Tasawaq-Niger",
		"dje-NE": "Zarma-Niger",
		"en-NG": "English-Nigeria",
		"ff-NG": "Fulah-Nigeria",
		"ha-NG": "Hausa-Nigeria",
		"ig-NG": "Igbo-Nigeria",
		"kaj-NG": "Jju-Nigeria",
		"kcg-NG": "Tyap-Nigeria",
		"yo-NG": "Yoruba-Nigeria",
		"en-NU": "English-Niue",
		"en-NF": "English-Norfolk Island",
		"ko-KP": "Korean-North Korea",
		"sq-MK": "Albanian-North Macedonia",
		"mk-MK": "Macedonian-North Macedonia",
		"en-MP": "English-Northern Mariana Islands",
		"en-NO": "English-Norway",
		"se-NO": "Northern Sami-Norway",
		"nb-NO": "Norwegian Bokmål-Norway",
		"nn-NO": "Norwegian Nynorsk-Norway",
		"ar-OM": "Arabic-Oman",
		"en-PK": "English-Pakistan",
		"ps-PK": "Pashto-Pakistan",
		"pa-PK": "Punjabi-Pakistan",
		"sd-PK": "Sindhi-Pakistan",
		"ur-PK": "Urdu-Pakistan",
		"en-PW": "English-Palau",
		"ar-PS": "Arabic-Palestinian Territories",
		"es-PA": "Spanish-Panama",
		"en-PG": "English-Papua New Guinea",
		"gn-PY": "Guarani-Paraguay",
		"es-PY": "Spanish-Paraguay",
		"qu-PE": "Quechua-Peru",
		"es-PE": "Spanish-Peru",
		"ceb-PH": "Cebuano-Philippines",
		"en-PH": "English-Philippines",
		"fil-PH": "Filipino-Philippines",
		"es-PH": "Spanish-Philippines",
		"en-PN": "English-Pitcairn Islands",
		"en-PL": "English-Poland",
		"pl-PL": "Polish-Poland",
		"en-PT": "English-Portugal",
		"pt-PT": "Portuguese-Portugal",
		"en-PR": "English-Puerto Rico",
		"es-PR": "Spanish-Puerto Rico",
		"ar-QA": "Arabic-Qatar",
		"fr-RE": "French-Réunion",
		"en-RO": "English-Romania",
		"ro-RO": "Romanian-Romania",
		"ba-RU": "Bashkir-Russia",
		"ce-RU": "Chechen-Russia",
		"cv-RU": "Chuvash-Russia",
		"en-RU": "English-Russia",
		"myv-RU": "Erzya-Russia",
		"os-RU": "Ossetic-Russia",
		"ru-RU": "Russian-Russia",
		"sah-RU": "Sakha-Russia",
		"tt-RU": "Tatar-Russia",
		"en-RW": "English-Rwanda",
		"fr-RW": "French-Rwanda",
		"rw-RW": "Kinyarwanda-Rwanda",
		"en-WS": "English-Samoa",
		"it-SM": "Italian-San Marino",
		"pt-ST": "Portuguese-São Tomé & Príncipe",
		"ar-SA": "Arabic-Saudi Arabia",
		"en-SA": "English-Saudi Arabia",
		"fr-SN": "French-Senegal",
		"ff-SN": "Fulah-Senegal",
		"dyo-SN": "Jola-Fonyi-Senegal",
		"wo-SN": "Wolof-Senegal",
		"en-RS": "English-Serbia",
		"sr-RS": "Serbian-Serbia",
		"en-SC": "English-Seychelles",
		"fr-SC": "French-Seychelles",
		"en-SL": "English-Sierra Leone",
		"ff-SL": "Fulah-Sierra Leone",
		"zh-SG": "Chinese-Singapore",
		"en-SG": "English-Singapore",
		"ms-SG": "Malay-Singapore",
		"ta-SG": "Tamil-Singapore",
		"nl-SX": "Dutch-Sint Maarten",
		"en-SX": "English-Sint Maarten",
		"es-SX": "Spanish-Sint Maarten",
		"en-SK": "English-Slovakia",
		"sk-SK": "Slovak-Slovakia",
		"en-SI": "English-Slovenia",
		"sl-SI": "Slovenian-Slovenia",
		"en-SB": "English-Solomon Islands",
		"ar-SO": "Arabic-Somalia",
		"so-SO": "Somali-Somalia",
		"af-ZA": "Afrikaans-South Africa",
		"en-ZA": "English-South Africa",
		"nso-ZA": "Northern Sotho-South Africa",
		"nr-ZA": "South Ndebele-South Africa",
		"st-ZA": "Southern Sotho-South Africa",
		"ss-ZA": "Swati-South Africa",
		"ts-ZA": "Tsonga-South Africa",
		"tn-ZA": "Tswana-South Africa",
		"ve-ZA": "Venda-South Africa",
		"xh-ZA": "Xhosa-South Africa",
		"zu-ZA": "Zulu-South Africa",
		"en-KR": "English-South Korea",
		"ko-KR": "Korean-South Korea",
		"ar-SS": "Arabic-South Sudan",
		"en-SS": "English-South Sudan",
		"nus-SS": "Nuer-South Sudan",
		"ast-ES": "Asturian-Spain",
		"eu-ES": "Basque-Spain",
		"ca-ES": "Catalan-Spain",
		"gl-ES": "Galician-Spain",
		"es-ES": "Spanish-Spain",
		"si-LK": "Sinhala-Sri Lanka",
		"ta-LK": "Tamil-Sri Lanka",
		"fr-BL": "French-St. Barthélemy",
		"es-BL": "Spanish-St. Barthélemy",
		"en-SH": "English-St. Helena",
		"en-KN": "English-St. Kitts & Nevis",
		"es-KN": "Spanish-St. Kitts & Nevis",
		"en-LC": "English-St. Lucia",
		"es-LC": "Spanish-St. Lucia",
		"fr-MF": "French-St. Martin",
		"es-MF": "Spanish-St. Martin",
		"fr-PM": "French-St. Pierre & Miquelon",
		"es-PM": "Spanish-St. Pierre & Miquelon",
		"en-VC": "English-St. Vincent & Grenadines",
		"es-VC": "Spanish-St. Vincent & Grenadines",
		"ar-SD": "Arabic-Sudan",
		"en-SD": "English-Sudan",
		"nl-SR": "Dutch-Suriname",
		"es-SR": "Spanish-Suriname",
		"nb-SJ": "Norwegian Bokmål-Svalbard & Jan Mayen",
		"en-SE": "English-Sweden",
		"se-SE": "Northern Sami-Sweden",
		"sv-SE": "Swedish-Sweden",
		"en-CH": "English-Switzerland",
		"fr-CH": "French-Switzerland",
		"de-CH": "German-Switzerland",
		"it-CH": "Italian-Switzerland",
		"pt-CH": "Portuguese-Switzerland",
		"rm-CH": "Romansh-Switzerland",
		"gsw-CH": "Swiss German-Switzerland",
		"wae-CH": "Walser-Switzerland",
		"ar-SY": "Arabic-Syria",
		"fr-SY": "French-Syria",
		"syr-SY": "Syriac-Syria",
		"zh-TW": "Chinese-Taiwan",
		"en-TW": "English-Taiwan",
		"trv-TW": "Taroko-Taiwan",
		"tg-TJ": "Tajik-Tajikistan",
		"asa-TZ": "Asu-Tanzania",
		"bez-TZ": "Bena-Tanzania",
		"en-TZ": "English-Tanzania",
		"lag-TZ": "Langi-Tanzania",
		"jmc-TZ": "Machame-Tanzania",
		"kde-TZ": "Makonde-Tanzania",
		"mas-TZ": "Masai-Tanzania",
		"rof-TZ": "Rombo-Tanzania",
		"rwk-TZ": "Rwa-Tanzania",
		"sbp-TZ": "Sangu-Tanzania",
		"ksb-TZ": "Shambala-Tanzania",
		"sw-TZ": "Swahili-Tanzania",
		"vun-TZ": "Vunjo-Tanzania",
		"en-TH": "English-Thailand",
		"th-TH": "Thai-Thailand",
		"pt-TL": "Portuguese-Timor-Leste",
		"ee-TG": "Ewe-Togo",
		"fr-TG": "French-Togo",
		"en-TK": "English-Tokelau",
		"en-TO": "English-Tonga",
		"to-TO": "Tongan-Tonga",
		"en-TT": "English-Trinidad & Tobago",
		"es-TT": "Spanish-Trinidad & Tobago",
		"ar-TN": "Arabic-Tunisia",
		"fr-TN": "French-Tunisia",
		"en-TR": "English-Turkey",
		"ku-TR": "Kurdish-Turkey",
		"tr-TR": "Turkish-Turkey",
		"tk-TM": "Turkmen-Turkmenistan",
		"en-TC": "English-Turks & Caicos Islands",
		"es-TC": "Spanish-Turks & Caicos Islands",
		"en-TV": "English-Tuvalu",
		"en-UM": "English-U.S. Outlying Islands",
		"en-VI": "English-U.S. Virgin Islands",
		"es-VI": "Spanish-U.S. Virgin Islands",
		"cgg-UG": "Chiga-Uganda",
		"en-UG": "English-Uganda",
		"lg-UG": "Ganda-Uganda",
		"nyn-UG": "Nyankole-Uganda",
		"xog-UG": "Soga-Uganda",
		"sw-UG": "Swahili-Uganda",
		"teo-UG": "Teso-Uganda",
		"en-UA": "English-Ukraine",
		"ru-UA": "Russian-Ukraine",
		"uk-UA": "Ukrainian-Ukraine",
		"ar-AE": "Arabic-United Arab Emirates",
		"en-AE": "English-United Arab Emirates",
		"kw-GB": "Cornish-United Kingdom",
		"en-GB": "English-United Kingdom",
		"gd-GB": "Scottish Gaelic-United Kingdom",
		"cy-GB": "Welsh-United Kingdom",
		"chr-US": "Cherokee-United States",
		"en-US": "English-United States",
		"haw-US": "Hawaiian-United States",
		"lkt-US": "Lakota-United States",
		"es-US": "Spanish-United States",
		"es-UY": "Spanish-Uruguay",
		"uz-UZ": "Uzbek-Uzbekistan",
		"en-VU": "English-Vanuatu",
		"fr-VU": "French-Vanuatu",
		"it-VA": "Italian-Vatican City",
		"es-VE": "Spanish-Venezuela",
		"vi-VN": "Vietnamese-Vietnam",
		"fr-WF": "French-Wallis & Futuna",
		"ar-EH": "Arabic-Western Sahara",
		"ar-001": "Arabic-World",
		"en-001": "English-World",
		"eo-001": "Esperanto-World",
		"io-001": "Ido-World",
		"ia-001": "Interlingua-World",
		"jbo-001": "Lojban-World",
		"yi-001": "Yiddish-World",
		"ar-YE": "Arabic-Yemen",
		"bem-ZM": "Bemba-Zambia",
		"en-ZM": "English-Zambia",
		"en-ZW": "English-Zimbabwe",
		"nd-ZW": "North Ndebele-Zimbabwe",
		"sn-ZW": "Shona-Zimbabwe"
}

async def get_available_voices():
    """Fetch available voices from edge_tts and organize them by language."""
    try:
        voices = await edge_tts.list_voices()
        # Organize voices by language and simplify voice names
        voices_by_language = {}
        for voice in voices:
            language_code = voice["Locale"]
            if language_code not in voices_by_language:
                voices_by_language[language_code] = []
            # Simplify the voice name (e.g., "Jenny" instead of "en-US-JennyNeural")
            voice_name = voice["ShortName"].split("-")[-1]  # Extract "Jenny" from "en-US-JennyNeural"
            voices_by_language[language_code].append({
                "ShortName": voice["ShortName"],
                "FriendlyName": voice_name
            })
        return voices_by_language
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return {}

@app.route("/")
def home():
    """Serve the HTML page with languages and voices."""
    # Fetch voices dynamically and organize them by language
    voices_by_language = loop.run_until_complete(get_available_voices())

    # Filter LANGUAGE_NAMES to include only languages with available voices
    filtered_languages = {
        code: name for code, name in LANGUAGE_NAMES.items() if code in voices_by_language
    }

    return render_template("index.html", languages=filtered_languages, voices_by_language=voices_by_language)

@app.route("/speak", methods=["POST"])
def speak():
    """API endpoint to generate and return speech audio."""
    data = request.get_json()
    text = data.get("text", "")
    voice = data.get("voice", "en-US-JennyNeural")  # Default voice

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Generate a unique filename
    unique_id = str(uuid.uuid4())
    output_file = f"output_{unique_id}.mp3"

    # Generate speech
    success = loop.run_until_complete(generate_speech(text, voice, output_file))

    if not success or not os.path.exists(output_file):
        return jsonify({"error": "Failed to generate speech"}), 500

    # Return the generated audio file as a stream
    response = send_file(
        output_file,
        as_attachment=False,  # Do not treat as a download
        mimetype="audio/mpeg"
    )

    # Delete the file after sending it
    @response.call_on_close
    def delete_file():
        try:
            os.remove(output_file)
        except Exception as e:
            print(f"Error deleting file: {e}")

    return response

async def generate_speech(text, voice, output_file):
    """Generate speech and save it as an MP3 file."""
    try:
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(output_file)
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

@app.route("/cleanup", methods=["POST"])
def cleanup():
    """Clean up generated audio files."""
    try:
        for file in os.listdir("."):
            if file.startswith("output_") and file.endswith(".mp3"):
                os.remove(file)
        return jsonify({"message": "Cleanup successful"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to clean up: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
