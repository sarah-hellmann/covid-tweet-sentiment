import dash_html_components as html
import dash_bootstrap_components as dbc

ian = 'static/img/Ian.jpg'
sarah = 'static/img/Sarah_photo.jpg'
zander = 'static/img/Zander_pic.jpg'
sam = 'static/img/picture_Sam.png'


layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("About"), 
                html.P("describe your company"),
                ],
                className='mx-2 my-2'
            )
        ]),
        dbc.Row([
            dbc.Col(html.H2("Team"), className='mx-2 my-2')
        ]),
        dbc.Row([
            dbc.Col(  
                dbc.Card(
                    dbc.Row([
                        dbc.Col(html.Img(src=sam, className="img-fluid"), className='col-3'),
                        dbc.Col([
                            html.H3('Kiriane Chikhaoui'),
                            html.P('Kiriane Samir Chikhaoui is in his first year of the Masters of Business Analytics at Tulane University. He transferred from Xavier University where he was part of the tennis team, NAIA national championship runner-up in 2019. He graduated with a B.S in Finance and accounting, double major with an overall 3.96 GPA. He currently works as the Changemaker Institute Graduate Assistant at the Taylor Center as well as a Data Analyst Intern at Phelps Dunbar. He is driven by new ideas, new technologies, and innovation, and is especially passionate about innovation in the Energy and A.I sectors.')
                            ],
                            className='col-9'
                        )
                    ])
                ),
                className="col-6 mx-2 my-2"
            )
        ]),
        dbc.Row([
            dbc.Col(  
                dbc.Card(
                    dbc.Row([
                        dbc.Col(html.Img(src=ian, className="img-fluid"), className='col-3'),
                        dbc.Col([
                            html.H3('Ian Eustis'),
                            html.P('Ian hails from New Orleans and is excited for a spring filled with crawfish and vaccines. Ian has two small children who keep him busy when hes not working and studying. ')
                            ],
                            className='col-9'
                        )
                    ])
                ),
                className="col-6 mx-2 my-2"
            )
        ]),
        dbc.Row([
            dbc.Col(  
                dbc.Card(
                    dbc.Row([
                        dbc.Col(html.Img(src=zander, className="img-fluid"), className='col-3'),
                        dbc.Col([
                            html.H3('Zander Hildreth'),
                            html.P('Alexander Hildreth is from New Orleans where he is a first year MANA student at Tulane University.  He attended undergrad at Louisiana State University and obtained his B.S in Agricultural Business.')
                            ],
                            className='col-9'
                        )
                    ])
                ),
                className="col-6 mx-2 my-2"
            )
        ]),
        dbc.Row([
            dbc.Col(  
                dbc.Card(
                    dbc.Row([
                        dbc.Col(html.Img(src=sarah, className="img-fluid"), className='col-3'),
                        dbc.Col([
                            html.H3('Sarah Hellmann'),
                            html.P('Sarah Hellmann is a second-semester MANA student at Tulane University. She graduated from Tulane University previously with a B.S.M in Finance and Legal Studies and is originally from New Jersey.')
                            ],
                            className='col-9'
                        )
                    ])
                ),
                className="col-6 mx-2 my-2"
            )
        ])
    ])
])
