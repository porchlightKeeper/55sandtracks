import random
import re
from typing import List
from flask import render_template_string, url_for
import markdown

NORMAL_FONT = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?"
FONTS = [
    "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꂵꈤꂦꉣꆰꋪꌗ꓄ꀎꃴꅏꊼꌩꁴ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ɐqɔpǝɟɓɥıɾʞlɯuodbɹsʇnʌʍxʎz∀ᙠƆᗡƎℲ⅁HIſ⋊˥WNOԀΌᴚS⊥∩ΛMX⅄Z ̖⇂ᄅƐㄣގ9ㄥ860-=][\؛,'˙/~¡@#$% ̮⅋*)(¯+}{|:„><¿",
    "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬאץչค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬאץչ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ǟɮƈɖɛʄɢɦɨʝӄʟʍռօքզʀֆȶʊʋաӼʏʐǟɮƈɖɛʄɢɦɨʝӄʟʍռօքզʀֆȶʊʋաӼʏʐ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ᏗᏰፈᎴᏋᎦᎶᏂᎥᏠᏦᏝᎷᏁᎧᎮᎤᏒᏕᏖᏬᏉᏇጀᎩፚᏗᏰፈᎴᏋᎦᎶᏂᎥᏠᏦᏝᎷᏁᎧᎮᎤᏒᏕᏖᏬᏉᏇጀᎩፚ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ąცƈɖɛʄɠɧıʝƙƖɱŋơ℘զཞʂɬų۷ῳҳყʑąცƈɖɛʄɠɧıʝƙƖɱŋơ℘զཞʂɬų۷ῳҳყʑ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ค๖¢໓ēfງhiวkl๓ຖ໐p๑rŞtนงຟxฯຊค๖¢໓ēfງhiวkl๓ຖ໐p๑rŞtนงຟxฯຊ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ΛBᄃDΣFGΉIJKᄂMПӨPQЯƧƬЦVЩXYZΛBᄃDΣFGΉIJKᄂMПӨPQЯƧƬЦVЩXYZ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "αв¢∂єƒgнιנкℓмησρqяѕтυνωχуzαв¢∂єƒgнιנкℓмησρqяѕтυνωχуz`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "åß¢Ðê£ghïjklmñðþqr§†µvwx¥zÄßÇÐÈ£GHÌJKLMñÖþQR§†ÚVW×¥Z`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫ₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ąҍçժҽƒցհìʝҟӀʍղօքզɾʂէմѵա×վՀȺβ↻ᎠƐƑƓǶįلҠꝈⱮហටφҨའϚͲԱỼచჯӋɀ`𝟙ϩӠ५ƼϬ7𝟠९⊘-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
    "ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭YᘔᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭Yᘔ`1234567890-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?",
]


def cool_font(text: str) -> str:
    font = random.choice(NORMAL_FONT)
    for i in range(len(NORMAL_FONT)):
        text = text.replace(NORMAL_FONT[i], font[i])
    return text


def render_markdown(text: str):
    html_content = markdown.markdown(text)
    return render_template_string('{{ content|safe }}', content=html_content)


def link_subjects_in_text(text: str, subjects: List[str]):
    """
    Replace occurrences of subject names in the provided text with hyperlinks to their respective paths.

    :param text: The text in which subject names are to be replaced with hyperlinks.
    :param subjects: A list of subject names.
    :return: The modified text with subject names replaced with hyperlinks.
    """
    print("linking")
    print(subjects)
    for subject in subjects:
        safe_subject = text_to_subject(text)
        url = url_for('new_article', subject=safe_subject)
        text = text.replace(subject, f"[{subject}]({url})")
    return text


def text_to_subject(text: str) -> str:
    """
    Replaces spaces with hyphens, and converts to lowercase.

    Also removes other unsafe chars.

    :param text: The input text to be converted.
    :return: A safe string.
    """
    text = text.strip()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-zA-Z0-9-_]', '', text)
    return text.lower()  # Convert to lowercase for consistency


def subject_to_text(subject: str) -> str:
    """
    Replaces hyphens with spaces.

    :param subject: The subject string with hyphens.
    :return: The text representation of the subject with hyphens replaced by spaces.
    """
    return subject.replace('-', ' ')
