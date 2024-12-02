import xml.etree.ElementTree as ET
from datetime import datetime
import re
import html

def clean_html_content(content):
    if content is None:
        return ''
    content = content.replace('<![CDATA[', '').replace(']]>', '')
    content = content.replace("'", "''")
    return content

def convert_wp_date(wp_date):
    dt = datetime.strptime(wp_date, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def extract_first_image(content):
    img_pattern = r'<img[^>]+src="([^">]+)"'
    match = re.search(img_pattern, content)
    if match:
        return match.group(1)
    return None

def get_post_views(item):
    for meta in item.findall('.//wp:postmeta', {'wp': 'http://wordpress.org/export/1.2/'}):
        meta_key = meta.find('wp:meta_key', {'wp': 'http://wordpress.org/export/1.2/'})
        if meta_key is not None and meta_key.text == '_eael_post_view_count':
            meta_value = meta.find('wp:meta_value', {'wp': 'http://wordpress.org/export/1.2/'})
            return meta_value.text if meta_value is not None else '0'
    return '0'

def generate_sql(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    sql_statements = []
    sql_template = """INSERT INTO `artikel` (`id`, `config_id`, `gambar`, `isi`, `enabled`, `tgl_upload`, `id_kategori`, `id_user`, `judul`, `headline`, `gambar1`, `gambar2`, `gambar3`, `dokumen`, `link_dokumen`, `boleh_komentar`, `slug`, `hit`, `tampilan`, `slider`, `tipe`) VALUES
    (NULL, 1, '{image}', '{content}', 1, '{date}', 1, 1, '{title}', 0, NULL, NULL, NULL, NULL, NULL, 1, '{slug}', {hit}, 1, 0, 'dinamis');"""

    for item in root.findall('.//item'):
        title = clean_html_content(item.find('title').text)
        content = clean_html_content(item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text)
        slug = clean_html_content(item.find('wp:post_name', {'wp': 'http://wordpress.org/export/1.2/'}).text)
        date = convert_wp_date(item.find('wp:post_date', {'wp': 'http://wordpress.org/export/1.2/'}).text)
        hit_count = get_post_views(item)
        image = extract_first_image(content) or ''
        
        sql = sql_template.format(
            title=title,
            slug=slug,
            content=content,
            date=date,
            image=image,
            hit=hit_count
        )
        sql_statements.append(sql)
    
    return '\n'.join(sql_statements)

# Usage
xml_file = 'c:\\Users\\user\\Downloads\\desapanjalu.WordPress.2024-12-02.xml'
output_file = 'artikel_import.sql'

with open(output_file, 'w', encoding='utf-8') as f:
    sql = generate_sql(xml_file)
    f.write(sql)
