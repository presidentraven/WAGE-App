#!/usr/bin/env python3
"""Bundle the latest validated snapshot into a standalone and hosted HTML dashboard."""
import csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
arch=json.loads((ROOT/'data/historical_events.json').read_text())
feed=json.loads((ROOT/'data/current.json').read_text())
assert feed['schema_version']==1 and len(feed['fuel'])>=197
p=(ROOT/'app_template.html').read_text()
sources=[{'title':'EIA — Chicago regular gasoline','url':'https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?f=W&n=PET&s=EMM_EPMR_PTE_YORD_DPG','note':'Regional weekly measured estimates; NOT individual daily ZIP-code prices.'},{'title':'Illinois Department of Labor — Minimum wage','url':'https://labor.illinois.gov/faqs/minimum-wage-overtime-faq.html','note':'Historical general minimum wage; scope and exceptions apply.'},{'title':'Illinois paid leave','url':'https://labor.illinois.gov/faqs/paidleavefaq.html','note':'Effective 2024; qualifying workers only.'},{'title':'MIT living wage — Will County','url':'https://livingwage.mit.edu/counties/17197','note':'County benchmark, periodic not daily.'},{'title':'IDOT Road Closures','url':'https://idot.illinois.gov/travel-and-maps/roadways/road-closures.html','note':'Dated notices; not route-time observations.'}]
for key, data in [('FUEL_JSON',feed['fuel']),('POLICIES_JSON',arch['policies']),('ROAD_JSON',arch['construction']),('SOURCES_JSON',sources),('WAGES_JSON',arch['minimum_wage'])]:
    p=p.replace('/*'+key+'*/',json.dumps(data,separators=(',',':')).replace('</','<\\/'))
# Initial embedded report date updates when a verified automated run is available.
p=p.replace("let AS_OF='2026-10-09';","let AS_OF="+json.dumps(feed['as_of'])+";")
(ROOT/'index.html').write_text(p,encoding='utf-8')
print('Built',ROOT/'index.html','size',len(p),'bytes')
