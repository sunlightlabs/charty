
from charty import Column, Line, Pie

g = Column( 600, 300, 
                [
                    [('aaaaaaaaaa', 'Subsidy Spending Unknown'), 
                     ('bbbbbbbbbb',800)
                    ], 
                    [('aaaaaaaaaa',230), 
                     ('bbbbbbbbbb',260), 
                     ('cccc', 300)
                    ]
                ], 
                "css/barchart.css", 
                label_rotate=-45, 
                y_padding=30
            )

g.output("svg/bar.svg")

h = Column( 600, 300, 
                [
                    [(2000, 10), 
                     (2001, 30), 
                     (2002, 40), 
                     (2003, 50)
                    ], 
                    [(1990, 30),  
                     (1992, 40), 
                     (2004, 50)
                    ]
                ], 
                'css/barchart.css', 
                label_intervals=2, 
                x_padding=15
            )
h.output("svg/line.svg")

h = Pie( 500, 500, 
            [
                [(2000, 1230), 
                 (2001, 3230), 
                 (2002, 4000), 
                 (2003, 1250), 
                 (2004, 1000), 
                 (2005, 1200), 
                 (2006, 800), 
                 (2007, 100), 
                 (22, 2332), 
                 (30, 3234)
                ]
            ], 
            'css/piechart.css', 
            y_padding=70, 
            x_padding=70
        )

h.output("svg/pie.svg")


#risk transfers
risk_transfers = Column( 370, 185, 
                            [
                                [('Outstanding Credit', 7445983679), 
                                 ('Subsidy', 114141251)
                                ]
                            ], 
                            "css/barchart.css", 
                            padding=10, 
                            currency=True
                       )

risk_transfers.output("svg/risk_transfers.svg")

#contracts

contracts = Line( 515, 330, 
                    [
                        [(2000, 12972951342), 
                         (2001, 14109441817), 
                         (2002, 15780150198), 
                         (2003, 20911608531), 
                         (2004, 21064466760), 
                         (2005, 15275901189)
                        ], 
                        [(2005, 15275901189), 
                         (2006, 15939230914), 
                         (2007, 19124684255), 
                         (2008, 18239197959), 
                         (2009, 16226290107)
                        ]
                    ], 
                    'css/linechart.css', 
                    label_intervals=3, 
                    x_padding=40, 
                    units=True, 
                    currency=True
                )
contracts.output("svg/contracts.svg")
