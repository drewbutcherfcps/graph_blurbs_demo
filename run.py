user_name = ''
password = ''
odbc_connection_name = ''

import re
import json
import pandas as pd
from sqlalchemy import create_engine

connection_string = \
    'mssql+pyodbc://{user_name}:{password}@{odbc_connection_name}'\
    .format(user_name=user_name,
            password=password,
            odbc_connection_name=odbc_connection_name)

with open('./graphBlurbs.json', encoding='utf-8-sig') as json_file:
    graph_blurbs = json.load(json_file)

with open('./graphInterpretations.json', encoding='utf-8-sig') as json_file:
    graph_interpretations_json = json.load(json_file)

dataframe_content = []


for graph_blurb in graph_blurbs:
    for graph_type in graph_interpretations_json["contents"]:
        if graph_type["type"] == graph_blurb["chartType"]:
            description_html = graph_type["description"]
            how_to_read_html = graph_type["howToRead"]
            citation_html = graph_type["citation"]
            
    externalReferences_html = ""
    for externalReference in graph_blurb["externalReferences"]:
        externalReferences_html += \
            """<li><a href="{url}" target="_blank">{resourceName}</a></li>"""\
            .format(url=externalReference["url"],
                    resourceName=externalReference["resourceName"])

    subtitle =\
"""<div class="fcps-help" tabindex="0">Click for additional information
<i class="fa fa-info-circle" aria-hidden="true" style="font-size: 1.5em;">
    </i>
</div>
<div id="{id}" class="fcps-help-contents" tabindex="0" style="opacity:0;">
    <label for="checkbox-{id}-1" class="fcps-label">
        <h4>
            <span class="fcps-click-to-expand">
                <i class="fa fa-expand" aria-hidden="true"></i>
            </span> What story is this chart telling?
        </h4>
    </label>
    <input id="checkbox-{id}-1" class="fcps-help-checkbox" type="checkbox" />
    <div class="fcps-hidden-content">
        <h5>Summary</h5><p>{graphStory}</p>
    </div>

    <label for="checkbox-{id}-2" class="fcps-label">
        <h4>
            <span class="fcps-click-to-expand">
                <i class="fa fa-expand" aria-hidden="true">
                </i>
            </span>How do I interpret this <span style="white-space: nowrap;">plot?<sup>1</sup></span>
        </h4>
    </label>
    <input id="checkbox-{id}-2" class="fcps-help-checkbox" type="checkbox" />
    <div class="fcps-hidden-content">
        {description_html} {how_to_read_html} {citation_html}
    </div>

    <label for="checkbox-{id}-3" class="fcps-label">
        <h4>
            <span class="fcps-click-to-expand">
                <i class="fa fa-expand" aria-hidden="true"></i>
            </span> How to use these data.
        </h4>
    </label>
    <input id="checkbox-{id}-3" class="fcps-help-checkbox" type="checkbox" />
    <div class="fcps-hidden-content">
        <ol>
            <li>{dataQualityReason} <a target="_blank" href="{dataQualityLinkUrl}">{dataQualityLinkContent}</a></li>
            <li>If you need additional support in this area contact: <a href="mailto:{contactEmailWithDot}@yourdomain?subject={contactSubjectLine}">{contactEmail}</a> or others from the same office</li>
            <li>EX. (appropriate interpretation/use) - {goodUseOfVisualtiation}</li>
            <li>EX. (inappropriate interpretation/use) - {lookOutFor}</li>
        </ol>
    </div>
    <h4>Additional Resources</h4>
    <ul>
        {externalReferences_html}
    </ul>
</div>
    """.format(
        id=graph_blurb["id"],
        graphStory=graph_blurb["graphStory"],
        description_html=description_html,
        how_to_read_html=how_to_read_html,
        citation_html=citation_html,
        dataQualityReason=graph_blurb["dataQualityReason"],
        dataQualityLinkUrl=graph_blurb["dataQualityLinkUrl"],
        dataQualityLinkContent=graph_blurb["dataQualityLinkContent"],
        contactEmailWithDot='.'.join(graph_blurb["contactEmail"].split()),
        contactSubjectLine=graph_blurb["contactSubjectLine"],
        contactEmail=graph_blurb["contactEmail"],
        goodUseOfVisualtiation=graph_blurb["goodUseOfVisualization"],
        lookOutFor=graph_blurb["lookOutFor"],
        externalReferences_html=externalReferences_html)
    dataframe_content.append({'object_id': graph_blurb["id"], 'subtitle': subtitle})
df_with_new_subtitles = pd.DataFrame(dataframe_content)

print("Here is an example of the string that will be inserted into the subtitle = ", dataframe_content[0]['subtitle'])

engine = create_engine(connection_string)
con = engine.connect()
query_string = \
'''SELECT 
    object_id,
    CONVERT(VARCHAR(MAX), CONVERT(VARBINARY(MAX), OBJECT_PROPS)) as 'original_decoded_object_props'
FROM [DCV-DWH-DB01].[K12INTEL_PORTAL_DEV].K12INTEL_PORTAL.PTL_OBJECTS'''
rs = con.execute(query_string)
df_from_data_base = pd.DataFrame(rs.fetchall())
df_from_data_base.columns = rs.keys()
df_from_data_base['object_id'] = df_from_data_base['object_id'].astype(int)
df_with_new_subtitles['object_id'] = df_with_new_subtitles['object_id'].astype(int)
new_df = pd.merge(df_from_data_base, df_with_new_subtitles, on='object_id') 


def change_string_new(row):
    if (row['original_decoded_object_props'] is not None) and (row['subtitle'] is not None):
        pattern = re.compile(r'<property name="SUBTITLE">.*?</property>', re.MULTILINE|re.DOTALL)
        new_string = re.sub(pattern, 
            '<property name="SUBTITLE"><![CDATA[{}]]></property>'.format(row['subtitle']),
            row['original_decoded_object_props'])
        return new_string
    return None

new_df['new_decoded_object_props'] = new_df.apply(change_string_new, axis=1)
new_df.to_sql('table_blurbs', con, if_exists="replace")
query_string_create_column = \
'''ALTER TABLE table_blurbs 
    ADD original_binary_object_props VARBINARY(MAX) NULL, new_binary_object_props VARBINARY(MAX) NULL;'''
query_string_add_original_binary_object_props = \
'''UPDATE table_blurbs
SET original_binary_object_props = CONVERT(VARBINARY(MAX), original_decoded_object_props);'''
query_string_add_new_binary_object_props = \
'''UPDATE table_blurbs
SET new_binary_object_props = CONVERT(VARBINARY(MAX), new_decoded_object_props);'''
con.execute(query_string_create_column)
con.execute(query_string_add_original_binary_object_props)
con.execute(query_string_add_new_binary_object_props)

query_to_inject_into_portal_objects = \
'''
Update K12INTEL_PORTAL_DEV.K12INTEL_PORTAL.PTL_OBJECTS
 
Set K12INTEL_PORTAL_DEV.K12INTEL_PORTAL.PTL_OBJECTS.OBJECT_PROPS = match.new_binary_object_props
 
From (Select v.OBJECT_ID, v.OBJECT_PROPS, f.new_decoded_object_props, f.new_binary_object_props
           from K12INTEL_PORTAL_DEV.K12INTEL_PORTAL.PTL_OBJECTS v
           Inner Join table_blurbs f on v.OBJECT_ID = f.OBJECT_ID
           ) match
          
where K12INTEL_PORTAL_DEV.K12INTEL_PORTAL.PTL_OBJECTS.OBJECT_ID = match.OBJECT_ID
'''
con.execute(query_to_inject_into_portal_objects)

con.close()
print("finished :)")    
