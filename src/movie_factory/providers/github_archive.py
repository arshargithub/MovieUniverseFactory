"""Trusted GitHub archival boundary; credentials never enter Blender or output."""
from __future__ import annotations
import json,re,subprocess,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from ..settings import load_settings


def inspect_destination(repo: Path) -> dict:
    settings=load_settings(repo)
    destination=settings.get('GITHUB_REPOSITORY','').strip()
    if destination.startswith('https://github.com/'):
        destination=urllib.parse.urlsplit(destination).path.strip('/')
    if destination.endswith('.git'):destination=destination[:-4]
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',destination):
        raise ValueError('GitHub repository setting must be owner/name')
    token=settings.get('GH_TOKEN','')
    if not token:raise ValueError('GitHub credential unavailable')
    def read(path):
        request=urllib.request.Request('https://api.github.com/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'MovieFactory-evidence-archive'})
        try:
            with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
        except urllib.error.HTTPError as error:raise RuntimeError('GitHub metadata request failed with HTTP '+str(error.code)) from None
    remote=subprocess.run(['git','remote','get-url','origin'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()
    expected=('https://github.com/'+destination+'.git','https://github.com/'+destination,'git@github.com:'+destination+'.git')
    metadata=read('repos/'+destination);user=read('user')
    outgoing=subprocess.run(['git','rev-list','--objects','origin/main..HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.splitlines()
    sensitive=[];secret_match=False
    secrets=[str(settings.get(key,'')) for key in ('GH_TOKEN','OPENAI_API_KEY') if settings.get(key)]
    for item in outgoing:
        oid,_,path=item.partition(' ')
        if not path:continue
        if any(x in {'.env','.venv','.runtime'} for x in Path(path).parts) or (Path(path).name.startswith('.env.') and Path(path).name!='.env.example'):sensitive.append(path)
        kind=subprocess.run(['git','cat-file','-t',oid],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()
        if kind=='blob':
            blob=subprocess.run(['git','cat-file','blob',oid],cwd=repo,capture_output=True,check=True).stdout
            secret_match |= any(secret.encode() in blob for secret in secrets)
    return {'repository':metadata['full_name'],'private':metadata['private'],'owner':metadata['owner']['login'],'authenticated_user':user['login'],'owner_matches_user':metadata['owner']['login']==user['login'],'push_permission':metadata.get('permissions',{}).get('push',False),'origin_matches_configured_repository':remote in expected,'outgoing_object_count':len(outgoing),'private_path_count':len(sensitive),'known_credential_in_outgoing_blobs':secret_match}


def diagnose_authentication(repo: Path) -> dict:
    """Return source names and response codes only; never credential values."""
    import os,time
    from ..settings import _read_dotenv,ALIASES
    settings=load_settings(repo)
    file_settings=_read_dotenv(repo/'.env')
    local_settings=_read_dotenv(repo/'.env.local')
    aliases=sorted({name for name,canonical in ALIASES.items() if canonical=='GH_TOKEN' and name in os.environ}|({'GH_TOKEN'} if 'GH_TOKEN' in os.environ else set()))
    effective=settings.get('GH_TOKEN','')
    report={'environment_override_names':aliases,'env_file_token_present':bool(file_settings.get('GH_TOKEN')),'env_local_override_present':bool(local_settings.get('GH_TOKEN')),'effective_matches_env_file':effective==file_settings.get('GH_TOKEN'),'effective_has_surrounding_whitespace':effective!=effective.strip(),'effective_has_bearer_prefix':effective.lower().startswith('bearer '),'checks':[]}
    for label,token in [('effective',effective),('project_env',file_settings.get('GH_TOKEN',''))]:
        if label=='project_env' and token==effective:continue
        if not token:continue
        req=urllib.request.Request('https://api.github.com/user?mf_auth_check='+str(time.time_ns()),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'MovieFactory-evidence-archive','Cache-Control':'no-cache'})
        try:
            with urllib.request.urlopen(req,timeout=30) as response:
                data=json.load(response);report['checks'].append({'source':label,'http_status':response.status,'authenticated_user':data.get('login')})
        except urllib.error.HTTPError as error:
            report['checks'].append({'source':label,'http_status':error.code,'github_request_id_present':bool(error.headers.get('X-GitHub-Request-Id')),'response_date':error.headers.get('Date')})
    return report


def inspect_outgoing_payload(repo: Path) -> dict:
    settings=load_settings(repo)
    secrets=[str(settings.get(k,'')) for k in ('GH_TOKEN','OPENAI_API_KEY') if settings.get(k)]
    objects=subprocess.run(['git','rev-list','--objects','origin/main..HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.splitlines()
    forbidden=[];matches=0
    for item in objects:
        oid,_,path=item.partition(' ')
        if not path:continue
        if any(part in {'.env','.venv','.runtime'} for part in Path(path).parts) or (Path(path).name.startswith('.env.') and Path(path).name!='.env.example'):forbidden.append(path)
        if subprocess.run(['git','cat-file','-t',oid],cwd=repo,capture_output=True,text=True,check=True).stdout.strip()=='blob':
            blob=subprocess.run(['git','cat-file','blob',oid],cwd=repo,capture_output=True,check=True).stdout
            matches+=int(any(secret.encode() in blob for secret in secrets))
    return {'object_count':len(objects),'private_paths':forbidden,'blobs_containing_configured_credentials':matches,'passed':not forbidden and not matches}


def inspect_git_authenticated_destination(repo: Path) -> dict:
    import os
    settings=load_settings(repo)
    name=settings.get('GITHUB_REPOSITORY','').strip()
    if name.startswith('https://github.com/'):name=urllib.parse.urlsplit(name).path.strip('/')
    if name.endswith('.git'):name=name[:-4]
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',name):raise ValueError('Invalid destination')
    result=subprocess.run(['git','credential','fill'],cwd=repo,input='protocol=https\nhost=github.com\n\n',env={**os.environ,'GIT_TERMINAL_PROMPT':'0'},capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError('Existing Git credential unavailable')
    credential=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    token=credential.get('password','')
    if not token:raise RuntimeError('Existing Git credential unavailable')
    def read(path):
        request=urllib.request.Request('https://api.github.com/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'MovieFactory-evidence-archive'})
        try:
            with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
        except urllib.error.HTTPError as error:raise RuntimeError('Git-authenticated metadata HTTP '+str(error.code)) from None
    metadata=read('repos/'+name);user=read('user')
    return {'repository':metadata['full_name'],'private':metadata['private'],'owner':metadata['owner']['login'],'authenticated_user':user['login'],'push_permission':metadata.get('permissions',{}).get('push',False),'authentication_source':'existing Git credential helper; .env unchanged'}
