import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import glob as glob
import numpy as np
from astropy.io import fits

###
### input the data directory path 
###
dir_spectra = '/path/to/data/lite/' ## the lite version spectra
conflist = fits.open('/path/to/data/conflist.fits') ## path to conflist file
spAll = fits.open('/path/to/data/spAll-master.fits') ## path to spALL-master file

### css files
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', \
'//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css', \
'http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css', \
'https://use.fontawesome.com/releases/v5.13.0/css/all.css', \
'https://use.fontawesome.com/releases/v5.13.0/css/v4-shims.css', \
]

### important spectra lines to label in plots
spectral_lines = { 'Ha': [6564], 
                   'Hb': [4862],
                   'MgII': [2798],
                   'CIII': [1908],
                   'CIV': [1549],
                   'Lya': [1215],}

### wavelength plotting range
wave_min = 3750
wave_max = 11000

### starting the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### get object info
### organize by program, plateid, catalogid
programname = ['SDSS-RM','XMM-LSS','COSMOS','AQMES-Medium','AQMES-Wide','eFEDS1','eFEDS2']

### RM programs have multiple plateid under single designid 
### we use the designid to garuntee all spectra for the same object is included
designid = {}
designid['SDSS-RM'] = [15173]#['15171', '15172', '15173']
designid['XMM-LSS'] = [15000]#['15000', '15002']
designid['COSMOS'] = [15035]#['15038', '15071','15072']
for i in programname[3:]:
    designid[i] = np.array(np.unique(conflist[1].data['designid'][np.where(conflist[1].data['programname']==i)]))#,dtype=str)
#print (designid.type)

plateid = {}
for i in np.unique(conflist[1].data['designid']):
    plateid[i]=np.unique(conflist[1].data['plate'][np.where(conflist[1].data['designid']==i)])
#print (plateid)

catalogid = {}
for i in np.unique(conflist[1].data['designid']):
    for v in plateid[i]:
        catalogid[v] = np.unique(spAll[1].data['catalogid'][np.where(spAll[1].data['plate']==v)])[1:] ## remove the 0 
#print (catalogid)

### 
### the webpage layout 
###
app.layout = html.Div(className='container',children=[
    html.H2(children=['SDSSV-BHM Spectra Viewer']),

    html.Div([

        ## dropdown menu titles
        html.Div([
            html.H4(children=['Program'])
        ],style={"width": "33%",'display': 'inline-block'}),

        ## plate ID dropdown
        html.Div(children=[
             html.H4(children=['Design/Plate ID'])
        ],style={"width": "33%",'display': 'inline-block'}),

        ## catalog ID dropdown
        html.Div(children=[
             html.H4(children=['Catalog ID'])
        ],style={"width": "33%",'display': 'inline-block'}),

    ]),

    html.Div([

        ## dropdown menu for program/designid/catalogid
        html.Div([
        dcc.Dropdown(
            id='program_dropdown',
            options=[
                {'label': i, 'value': i} for i in designid.keys()],
            placeholder="Program",
            value='XMM-LSS',
            #style={'display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),

        ## plate ID dropdown
        html.Div(children=[
        dcc.Dropdown(
            id='plateid_dropdown',
            placeholder='Plate ID',
            #style={'width':'50%','display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),


        ## catalog ID dropdown
        html.Div(children=[
        dcc.Dropdown(
            id='catalogid_dropdown',
            placeholder='Catalog ID',
            #style={'width':'50%','display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),

    ]),

    ## multiepoch spectra plot
    dcc.Checklist(
        id="epoch_list",
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="spectra_plot"),

    html.Div([

    	## spectral binning
        html.Div(children=[
            html.H4(children=['Binning:'])
        ],style={"width": "10%",'display': 'inline-block'}),

        html.Div(children=[
            dcc.Input(id="binning_input", type="number", value=5),
        ],style={"width": "20%",'display': 'inline-block'}), 

        ## label important spectral lines
        html.Div(children=[
            html.H4(children=['Lines:'])
        ],style={"width": "10%",'display': 'inline-block'}),   

        html.Div(children=[
            dcc.Checklist(id="line_list",options=[
                {'label': i+' ('+str(int(spectral_lines[i][0]))+'A)', 'value': i} for i in spectral_lines.keys()
                ], 
                value=list(spectral_lines.keys())),
        ],style={"width": "60%", 'display': 'inline-block'}),    

    ]),
   
    ## TODO: print source information (ra, dec, z, etc...) from some catalog
    html.Div([
    	html.H5(id='property_text')

   	 ])

])


###
### interactive callback functions for updating spectral plot
###

## dropdown menu
@app.callback(
    Output('plateid_dropdown', 'options'),
    Input('program_dropdown', 'value'))
def set_plateid_options(selected_program):
    return [{'label': str(i)+' '+str(plateid[i]), 'value': i} for i in designid[selected_program]]

@app.callback(
    Output('catalogid_dropdown', 'options'),
    Input('plateid_dropdown', 'value'))
def set_catalogid_options(selected_designid):
    return [{'label': i, 'value': i} for i in catalogid[plateid[selected_designid][0]]]

@app.callback(
    Output('plateid_dropdown', 'value'),
    Input('plateid_dropdown', 'options'))
def set_plateid_value(available_plateid_options):
    return available_plateid_options[0]['value']

@app.callback(
    Output('catalogid_dropdown', 'value'),
    Input('catalogid_dropdown', 'options'))
def set_catalogid_value(available_catalogid_options):
    return available_catalogid_options[0]['value']


## plotting the spectra
@app.callback(
    Output('spectra_plot','figure'),
    Input('plateid_dropdown', 'value'),
    Input('catalogid_dropdown', 'value'),
    Input('binning_input', 'value'),
    Input('line_list', 'value'))
def make_multiepoch_spectra(selected_designid, selected_catalogid, binning, lines):
    filename = np.array([])
    mjd_tmp = np.array([])
    for i in plateid[selected_designid]:
        #print(dir_spectra+str(i)+'p/*/spec-'+str(i)+'-*-'+str(selected_catalogid).zfill(11)+'.fits')
        tmp = glob.glob(dir_spectra+str(i)+'p/*/spec-'+str(i)+'-*-'+str(selected_catalogid).zfill(11)+'.fits')
        #print(tmp)
        if len(tmp)>0: 
            filename = np.append(filename,tmp,axis=0)
            mjd_tmp = np.append(mjd_tmp,[f.split('/')[-2] for f in tmp],axis=0)

    epoch = np.array([])
    wave = np.array([])
    flux = np.array([])
    filename = [x for _,x in sorted(zip(mjd_tmp,filename))]  ## sort by mjd
    for f in filename:
        #print(f.split('/'))
        mjd = f.split('/')[-2]
        hdu = fits.open(f)
        plate = f.split('/')[-3][:5]
        #print(mjd, plate)
        epoch = np.append(epoch,np.zeros(len(hdu[1].data['flux']))+float(plate)+float(mjd)/1e5,axis=0)
        wave = np.append(wave,10**hdu[1].data['loglam'],axis=0)
        flux = np.append(flux,hdu[1].data['flux'],axis=0)
    #epoch = np.array(epoch,dtype=int)
    df = pd.DataFrame({'epoch':epoch,'wave':wave,'flux':flux})
    mask = ((df['wave']>wave_min) & (df['wave']<wave_max))
    fig = px.line(df[mask][::binning], x='wave', y='flux',color='epoch')

    ## TODO: plot important lines
    '''
    for l in lines:
        for ll in spectral_lines[l]:
            if ll > wave_min and ll < wave_max: 
                fig.add_vline(x=ll,line_width=1.5)
    '''

    #fig.update_layout(xaxis=dict(showline=True,showgrid=False,linecolor='black',ticks='inside',), \
    #	yaxis=dict(showline=True,showgrid=False,linecolor='black',ticks='inside',), \
    #	plot_bgcolor='white')
    return fig;

### setting the selected epochs for plotting
@app.callback(
    Output('epoch_list','value'),
    Input('plateid_dropdown', 'value'),
    Input('catalogid_dropdown', 'value'))
def set_epoch_value(selected_designid,selected_catalogid):
    filename = np.array([])
    for i in plateid[selected_designid]:
        tmp = glob.glob(dir_spectra+str(i)+'p/coadd/*/spSpec-'+str(i)+'-*-'+str(selected_catalogid).zfill(11)+'.fits')
        if len(tmp)>0: 
            filename = np.append(filename,tmp,axis=0)
    epoch = np.array([])
    for f in filename:
        mjd = f.split('/')[-2]
        plate = f.split('/')[-4][:5]
        epoch = np.append(epoch,float(plate)+float(mjd)/1e5)
    return [{'label':i, 'value':i} for i in epoch]

if __name__ == '__main__':
    app.run_server(debug=True)


