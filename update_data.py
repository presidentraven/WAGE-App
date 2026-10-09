#!/usr/bin/env python3
"""W.A.G.E. EIA fuel collector.
Network mode requires EIA_API_KEY in an environment variable, never a browser file.
Stale/invalid responses cause failure, retaining the last committed file.
"""
import argparse,csv,datetime as dt,json,os,pathlib,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
CSV=ROOT/'data/eia_chicago_weekly.csv'
STATE=ROOT/'data/current.json'
SERIES='EMM_EPMR_PTE_YORD_DPG'
EIA_URL='https://api.eia.gov/v2/petroleum/pri/gnd/data/'
HIST='https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?f=W&n=PET&s='+SERIES
HEAD=['date','type','value','unit','location','geography','frequency','source_url','observed_or_effective']

def check_rows(rows, today):
    if len(rows)<197:raise ValueError('Too few weekly records; refusing to overwrite archive')
    last=''
    for r in rows:
        d=dt.date.fromisoformat(r['date'])
        v=float(r['value'])
        if d.weekday()!=0 or r['date']<=last or d>today or not 1<=v<=12:raise ValueError('Invalid date/order/price: '+str(r))
        last=r['date']
    if rows[0]['date']!='2023-01-02':raise ValueError('Expected Jan 2023 baseline missing')
    if dt.date.fromisoformat(rows[-1]['date'])<dt.date(2026,10,5):raise ValueError('Latest dated observation precedes verified baseline')
    return rows

def read_existing():
    with CSV.open(newline='',encoding='utf-8') as f:
        return [{'date':r['date'],'value':float(r['value'])} for r in csv.DictReader(f)]

def fetch_eia(api_key,today):
    if not api_key:raise RuntimeError('EIA_API_KEY is required. Add it as a GitHub Actions repository secret.')
    params={'api_key':api_key,'frequency':'weekly','data[0]':'value','facets[series][]':SERIES,'start':'2023-01-01','end':today.isoformat(),'sort[0][column]':'period','sort[0][direction]':'asc','length':'5000'}
    url=EIA_URL+'?'+urllib.parse.urlencode(params)
    request=urllib.request.Request(url,headers={'User-Agent':'WAGE-joliet-prototype/0.3 (data compliance testing)'})
    with urllib.request.urlopen(request,timeout=30) as response:
        payload=json.load(response)
    if payload.get('response',{}).get('data') is None:raise ValueError('API did not return response.data')
    results=payload['response']['data']
    if any(r.get('series')!=SERIES for r in results):raise ValueError('EIA series mismatch')
    rows=[{'date':r['period'],'value':float(r['value'])} for r in results]
    rows.sort(key=lambda a:a['date'])
    return check_rows(rows,today)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--online',action='store_true',help='fetch EIA data using EIA_API_KEY');ap.add_argument('--offline',action='store_true',help='validate and package the saved baseline only');args=ap.parse_args()
    if args.online==args.offline:ap.error('Choose exactly one: --online or --offline')
    today=dt.datetime.now(dt.timezone.utc).date()
    # Never use network-generated data beyond the current day; single source, single geography.
    rows=fetch_eia(os.getenv('EIA_API_KEY',''),today) if args.online else check_rows(read_existing(),today)
    # Always keep source-dated values; never synthesize daily prices or duplicate weekly observations.
    with CSV.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(HEAD)
        for r in rows:writer.writerow([r['date'],'fuel',format(r['value'],'.3f'),'USD_per_gallon','Chicago metro','regional_proxy','weekly',HIST,'observed'])
    feed={'schema_version':1,'series':SERIES,'mode':'eia_api' if args.online else 'seed_only','as_of':today.isoformat() if args.online else '2026-10-09','checked_at':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),'fuel':rows,'source':HIST,'geography':'Chicago area (not 60432 station)','frequency':'weekly','unavailable':['zip_gas_daily','job_posting_history','traffic_delay_60_days']}
    STATE.write_text(json.dumps(feed,separators=(',',':'))+'\n',encoding='utf-8')
    print(f'Validated {len(rows)} original weekly EIA observations; latest {rows[-1]}; mode={feed["mode"]}')
if __name__=='__main__':main()
