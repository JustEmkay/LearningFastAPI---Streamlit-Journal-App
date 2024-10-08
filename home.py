import streamlit as st
import requests,time
from datetime import datetime as dt, time as t
from rich.console import Console
import bcrypt,hashlib,json
import streamlit.components.v1 as components
from pages.function.journal_graph import radar_graph


console = Console()

URL_API : str = "http://127.0.0.1:8000/"



if 'api_connect' not in st.session_state: st.session_state.api_connect = False
if 'error' not in st.session_state: st.session_state.error = False
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'user_journal' not in st.session_state: st.session_state.user_journal = None
if 'hash_journal' not in st.session_state: st.session_state.hash_journal = None
if 'journals' not in st.session_state: st.session_state.journals = {
    'status' : False ,
    'data' : [],
    'error' : 'Empty '
}
if 'temp_journal' not in st.session_state:st.session_state.temp_journal = {}
if 'settings' not in st.session_state:st.session_state.settings = {
    'predef' : []
}


tstamp_today : int = int(dt(dt.now().year,dt.now().month,dt.now().day,00,00,00).timestamp())


rating_aspects_list : list = [
            'mood',
    'productivity',
    'stress_level',
    'social_interaction',
    'energy_level'
]

SCALE : tuple = ('worst', 'poor', 'average', 'good', 'excellent')

def connect_api() -> bool:
    try:
        r = requests.get(URL_API+'connection')
        response = r.status_code
        if response == 200:
            return r.json()
        return False
        
    except requests.ConnectionError:
        st.error("Connection Error : API not running",icon='❗')
        if st.button("Retry"):
            st.rerun()
        return False
        
def send_get():
    r = requests.get(URL_API)
    response = r.status_code
    if response == 200:
        return r.json()
    return 'error occured'

def verify_email(username) -> bool:
    r = requests.post(URL_API+f'verify/user/{username}')
    response = r.status_code
    if response == 200:
        st.session_state.error = r.json()

def pass_hashing(password : str) -> str:
     
    bytes = password.encode('utf-8') 
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt) 

    return hash.decode('utf-8')

def data_hashing(data) -> str:
    """
    Get complex dictionaries and return Hash.

    Args:
        data (dict): dictionary.

    Returns:
        Hash value of dictionary.
        
    Example:
        data (str) = {
    'name' : 'emkay',
    'gender' : 'male',
    'hobbies' : ['scrabbling','gaming'],
    }
    
    output:
        0679b5848c062ab23a34a35f78b96833
        
    """
    
    dict_string = json.dumps(data, sort_keys=True).encode('utf-8')
    dict_hash = hashlib.md5(dict_string).hexdigest()
    return dict_hash
 
def login_req(username,password) -> dict:
    r = requests.post(URL_API+f'validate/{username}/{password}')
    response = r.status_code
    if response == 200:
        return r.json()

class Register:
    def __init__(self,uname,email,dob,password,re_password) -> None:
        self.uname = uname
        self.email = email
        self.dob = dob
        self.pswd = password
        self.rpswd = re_password
        self.predef = []
    
    def dob_to_timestamp(self) -> int:
        d_timestamp=int(dt(self.dob.year,self.dob.month,self.dob.day).timestamp())
        return d_timestamp
    
    def validate_username(self) -> dict:
        if not self.uname:
            return {'status': False, 'error': 'cant leave blank'} 
        r = requests.post(URL_API+f'verify/user/{self.uname}')
        response = r.status_code
        if response == 200:
            if not r.json():
                return {'status': False , 'error' : ':red[Username used by someone else]. Please change it' }
            else:
                return {'status': True }
    
    def validate_email(self) -> dict:
        if not self.email:
            return {'status': False, 'error': 'cant leave blank'} 
        r = requests.post(URL_API+f'verify/user/{self.email}')
        response = r.status_code
        if response == 200:
            if not r.json():
                return {'status': False , 'error' : ':red[Email already in use.] Please login using it.' }
            else:
                return {'status': True }
  
    def validate_password(self) -> str:
        
        if self.pswd == self.rpswd:
            return {'status': True , 'error' : None }
        elif not self.pswd:
            return {'status': False , 'error' : 'Please create a password' }
        elif not self.rpswd:
            return {'status': False , 'error' : 'Please re-enter new password' }
        else:
            return {'status': False , 'error' : 'Passwords not same' }
        
    def register_user(self) -> dict:
        temp_user :dict = {
                "username" : self.uname,     
                "email" : self.email,
                "dob": Register.dob_to_timestamp(self),
                "password": pass_hashing(self.pswd),
                "predef" : self.predef
            
        }
        r = requests.post(URL_API+f'register/{tstamp_today}',json=temp_user)
        response = r.status_code
        if response == 200:
            return r.json()
    
@st.dialog('Register your account')
def register_account() -> None:
    with st.form('user signup'):
        uname : str = st.text_input("Enter your username:",
                                    placeholder='Example: Vasu Annan')
        error_uname = st.empty()
           
        email : str = st.text_input("Enter your email:",
                                    placeholder='Example: vasu69@hotmail.com')
        error_email = st.empty()
        
        dob  = st.date_input("Select your dob:",min_value=dt(1940, 1, 1))
        
        
        pwsd : str = st.text_input("create new password:", type='password',
                                    placeholder='Example: Vasu@gojo')
        re_pwsd : str = st.text_input("re-enter the password:", type='password',
                                    placeholder='Example: Vasu@gojo')
        error_pwsd = st.empty()
        
        r = Register(uname,email,dob,pwsd,re_pwsd)
        if st.form_submit_button('Submit',use_container_width=True,type='primary'):
            
            u_val = r.validate_username()
            if not u_val['status']:
                error_uname.warning(u_val['error'],icon='⚠')
            
            e_val = r.validate_email()
            if not e_val['status']:
                error_email.warning(e_val['error'],icon='⚠')
            
            p_val = r.validate_password()
            if not p_val['status']:
                error_pwsd.warning(p_val['error'],icon='⚠')
            
            if u_val['status'] and e_val['status'] and p_val['status']:
                r_resp = r.register_user()
                if not r_resp['status']:
                  st.error(f"Error : {r_resp['error']}")
                else:
                    st.success("Registration Sccessful")  

class ManageJournal:
    def __init__(self,user_id,tstamp_today) -> None:
        self.id : int = user_id
        self.timestmp : int = tstamp_today

    def load_data(self) -> dict:
        r = requests.get(URL_API+f'journal/{self.id}/{self.timestmp}')
        response = r.status_code
        if response == 200:
            return r.json()
        return {}
    
    def update_data(self,data) -> dict:
        r = requests.post(URL_API+f'journal/{self.id}/{self.timestmp}',
                          json=data)
        response = r.status_code
        if response == 200:
            return r.json()
        
def journal_preview() -> None:
    with st.container(border=True):
        date_col, preview_col = st.columns([3,1],vertical_alignment='top')
        date_col.write(f'**Date:** :green[{dt.fromtimestamp(tstamp_today).strftime("%d-%m-%Y")}]')
    
    col1, col2 = st.columns([2,2]) 
    
    # agendas
    with col1.container(border=True,height=300):
        st.write("""**Today's Agendas:**""")
        counter : int = 0
        for i in st.session_state.user_journal['not_completed']:
            counter += 1
            st.markdown(f"""{counter}. {i}""")
            
        for j in st.session_state.user_journal['completed']:
            counter +=1
            st.markdown(f"""{counter}. :grey[~{j}~]""")
        counter = 0
        if not st.session_state.user_journal['not_completed'] + st.session_state.user_journal['completed']:
            st.markdown(f""":grey[***Lazzzyyyyy***]""")
    # rating
    with col2.container(border=True,height=300):
        
        
        
        st.markdown("""**Rating:**""",help= "  ")
        for l in rating_aspects_list:
            if l in st.session_state.user_journal:
                if st.session_state.user_journal[l] > 0:
                    st.markdown(f"""* {l}  :green[{SCALE[(st.session_state.user_journal[l]-1)]}]""")
                else:
                    st.markdown(f"""* {l}  :red[Not Rated]""")
    # thankful
    with st.container(border=True):
        if st.session_state.user_journal['thankful']:
            st.markdown("""**Today, I'm Thankful for...**""")
            for k in st.session_state.user_journal['thankful']:
                st.markdown(f"""* {k}""")
        else:
            st.markdown("""**Today, I'm Thankful for...** ***Nothing***""")
    
    # lesson & s*cks
    with st.container(border=True):
        if st.session_state.user_journal['lessons']:
            st.markdown(f"""**Today's Lesson :** {st.session_state.user_journal['lessons']}
                    \n **One thing I did that sucked:** {st.session_state.user_journal['sucks']}""")
        else:
            st.markdown(f"""**Lessons :**  :grey[***Empty***]""")
    
def add_agenda() -> None:
    task_col, addBtn_col = st.columns([3,1])
    new_task : str = task_col.text_input('Task',value='',
                               label_visibility='collapsed',
                               placeholder='What you want to accomplish?',
                               help="Example: Go for a walk")
    with addBtn_col.popover('options',use_container_width=True):
        
        if st.button('Add',use_container_width=True,type='primary') and new_task:
            st.session_state.user_journal['not_completed'].append(new_task)
            st.rerun()
            
        
        if st.button('Delete',use_container_width=True,
                     help=':red-background[Delete all completed task]'):
            st.session_state.user_journal['completed'] = []
            st.rerun()

def add_thankful() -> None:
    thankful_col, add_col = st.columns([3,1])
    thankful : str = thankful_col.text_input('Thankful',value='',
                               label_visibility='collapsed',
                               placeholder='Today, I am thankful for .....',
                               help="Example: That im still alive 🙏")
    if add_col.button("add",use_container_width=True,
                      type='primary') and thankful:
        st.session_state.user_journal['thankful'].append(thankful)
        st.rerun()

def add_lessons() -> None:
    with st.container(border=True,height=500):
        if not st.session_state.user_journal['lessons']:
            lessons : str = st.text_area("Today's lessons ?",
                                        value=st.session_state.user_journal['lessons'],
                                        label_visibility='visible')
            bttn_name = 'add'
        else:
            st.write(st.session_state.user_journal['lessons'])
            bttn_name = 'update'
            
        if not st.session_state.user_journal['lessons']:   
            sucks : str = st.text_input('One thing I did that sucked:',
                                    value=st.session_state.user_journal['sucks'],
                                    label_visibility='visible')
        else:
            st.write(st.session_state.user_journal['sucks'])
            bttn_name = 'update'
            
        black_col,clear_bttn, bttn_col = st.columns([2,1,1])
        if clear_bttn.button('clear',use_container_width=True):
            st.session_state.user_journal['lessons'] = ''
            st.session_state.user_journal['sucks'] = ''
            time.sleep(1)
            st.rerun()

        if bttn_col.button(bttn_name,use_container_width=True,
                           type='primary',key='lesson_btn'):
            st.session_state.user_journal['lessons'] = lessons
            st.session_state.user_journal['sucks'] = sucks
            time.sleep(1)
            st.rerun()

def update_agenda(task_action : list ,task_id : int) -> bool:
    st.session_state.user_journal[task_action[0]].append(st.session_state.user_journal[task_action[1]][task_id])
    st.session_state.user_journal[task_action[1]].pop(task_id)
    return True

def agenda_box():
    add_agenda()
    cmpltd_col, ncmpltd_col = st.columns(2)
    ncmpltd : list = st.session_state.user_journal['not_completed']
    cmpltd : list = st.session_state.user_journal['completed']

    #---LEFT-AGENDA.CONTAINER---
    with cmpltd_col.container(border=True,height=400):
        st.write(':red-background[Not Completed❎]')
        if ncmpltd:
            for nid,ntask in enumerate(ncmpltd):
                if st.checkbox(ntask,key='n'+str(nid),value=False):
                    if update_agenda(['completed','not_completed'],nid):    
                        st.rerun()
        else:
            st.text('--Empty--')        
    #---RIGHT-AGENDA.CONTAINER---
    with ncmpltd_col.container(border=True,height=400):
        st.write(':green-background[Yes Completed✅]')
        if cmpltd: 
            for cid,ctask in enumerate(cmpltd):
                if not st.checkbox(ctask,key='c'+str(cid),value=True):
                    if update_agenda(['not_completed','completed'],cid):    
                        st.rerun()
        else:
            st.text('--Empty--') 
    
def thankful_box() -> None:
    add_thankful()
    
    thankful : dict = st.session_state.user_journal['thankful']
    
    with st.container(border=True,height=430):
        if thankful:
            for idx, thank in enumerate(thankful):
                if st.checkbox(f'{idx+1}.'+thank,key=idx,value=False):
                    with st.spinner('delete this note in 3s...'):
                        time.sleep(3)
                        st.session_state.user_journal['thankful'].pop(idx)
                        st.toast(':green-background[Deleted selected thank note]')
                        time.sleep(1)
                        st.rerun()
        else:
            st.text('--Empty--')

def lesson_box() -> None:
    lessons : str = st.session_state.user_journal['lessons']
    sucks : str = st.session_state.user_journal['sucks']
    add_lessons()
    
def rate_box() -> None:
    
    rating_aspects : dict = {}
    for  ral in rating_aspects_list:
        if ral in st.session_state.user_journal:
            rating_aspects.update({ral : st.session_state.user_journal[ral]})
    
    rate_col, graph_col = st.columns([0.4,0.6])

    md : int = rate_col.slider('Mood',min_value=0,
                        value=rating_aspects[rating_aspects_list[0]],
                         max_value=5,label_visibility='visible',
                         help="ddadawd") 
    
    prod : int = rate_col.slider('Productivity',min_value=0,
                        value=rating_aspects[rating_aspects_list[1]],
                        max_value=5,label_visibility='visible',
                        help="ddadawd") 
    
    
    sl : int = rate_col.slider('Stress level',min_value=0,
                        value=rating_aspects[rating_aspects_list[2]],
                         max_value=5,label_visibility='visible',
                         help="ddadawd") 
    
    si : int = rate_col.slider('Social Interaction',min_value=0,
                        value=rating_aspects[rating_aspects_list[3]],
                         max_value=5,label_visibility='visible',
                         help="ddadawd") 
    
    el : int = rate_col.slider('Energy level',min_value=0,
                        value=rating_aspects[rating_aspects_list[4]],                               
                         max_value=5,label_visibility='visible',
                         help="ddadawd") 
        
    with graph_col.container(border=True,height=500):
        fig = radar_graph(rating_aspects)
        fig.update_layout(height=400)
        st.plotly_chart(fig)

    new_aspects : list = [md,prod,sl,si,el]
    
    for  idx, aspect in enumerate(rating_aspects_list):
        if st.session_state.user_journal[aspect] != new_aspects[idx]:
            st.session_state.user_journal.update({aspect:new_aspects[idx]})
            st.toast(f'updated :green[**{aspect}**]')
            time.sleep(0.5)
            st.rerun()

def homepage() -> None:
    mj : object = ManageJournal(st.session_state.user_id,tstamp_today)
    if not st.session_state.user_journal:
        st.session_state.user_journal = mj.load_data()
        st.session_state.hash_journal = data_hashing(st.session_state.user_journal)
        st.spinner("Updating journal....")
        time.sleep(2)
        st.rerun()
    
    #---JOURNAL-CONTAINER---

    tabs : list[str] = ['Preview','Agenda','Thankful','Lessons','Rate']
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)
    
    with tab1:
        journal_preview()
    
    with tab2:
        agenda_box()
    
    with tab3:
        thankful_box()
    
    with tab4:
        lesson_box()
    
    with tab5:
        rate_box()
        
    if st.session_state.hash_journal != data_hashing(st.session_state.user_journal):

        result = mj.update_data(st.session_state.user_journal)
        if result['status']:
            st.session_state.user_journal = result['data']
            st.session_state.hash_journal = data_hashing(result['data'])
            st.toast(":green[Change applied to Database]")
            st.rerun()   
        else:
            st.toast(":red[Failed to update to Database]")
    
        
#--MAIN----
def main() -> None:
    
    # st.session_state.user_journal
    
    console.print(f'\n[ Executed: [bold magenta]{dt.today().time().strftime("%H:%M:%S")}[/bold magenta] ]')
    st.title('Journal',anchor=False)
    
    if not st.session_state.api_connect:
        with st.status("Sending Request to Server...") as status: 
            time.sleep(1)
            st.session_state.api_connect = connect_api()
            status.update(
                label="Waiting for response", state="running", expanded=False
            )
            time.sleep(1)
            if st.session_state.api_connect:
                status.update(label=":green[Connected]",
                              state="complete", expanded=True)
                time.sleep(1)
                st.success('Connection to API successful',icon='✔')
                st.rerun()
                
            status.update(label=":red[Not Connected]",
                            state="error", expanded=True)
            time.sleep(1)
            st.error('Failed Connection to API',icon='🚫')

    else:
        with st.sidebar:
            st.success('Connection to API successful',icon='✔')
        
        if st.session_state.auth and st.session_state.user_id:
            
            homepage()
            
        else:
            #login form
            with st.container(border=True):
                st.subheader('Login',anchor=False,divider=True)
                username =st.text_input("Username:",value='',
                                            placeholder="Enter your username",
                                            label_visibility='collapsed')
                password : str =st.text_input("Password:",value='',
                                            placeholder="Enter your password",
                                            label_visibility='collapsed',
                                            type='password')
                if username : verify_email(username)
                log_btn : bool = False
                if st.session_state.error:
                    st.warning('Email not found',icon='⚠')
                    log_btn : bool = True
                
                alert = st.empty()
                
                blank_col,reg_col,log_col = st.columns([2,1,1])
                if reg_col.button('register',use_container_width=True):
                    register_account()
                    
                if log_col.button('login',use_container_width=True,
                                type='primary',disabled=log_btn):
                    if username and password:
                        login_response : dict = login_req(username,password)
                        if login_response['error']:
                            alert.error(login_response['message'])    
                        elif login_response['auth'] and not login_response['error']: 
                            st.session_state.auth = login_response['auth']
                            st.session_state.user_id = login_response['user_id']
                            st.session_state.settings.update({
                                    'predef' : login_response['predef']
                                })  
                            st.success(login_response['message'])
                            st.spinner("Loading Homepage....")
                            time.sleep(2)
                            st.rerun()
            
    
if __name__ == "__main__":
    
    st.set_page_config(
    page_title="journal",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed",
)
    
    
    main()
    components.html("""
    <script>
    window.onbeforeunload = function() {
        return 'Are you sure you want to leave? You might lose unsaved data.';
    };
    </script>
    """, height=0)
