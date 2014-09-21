import matplotlib.pyplot as plt
import itertools


marker_symbols = "oxs^+v"

def plot_hrn(data, title, filename, xvalues=[5,10,15,30], xlabel="N", ylabel="Hit Ratio",**kwargs):
    markers = itertools.cycle(marker_symbols)
    plt.clf()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # legend position
    loc = "best"
    if "loc" in kwargs:
        loc = kwargs["loc"]
        del kwargs["loc"]

    for label, values in data:
        m = markers.next()
        plt.plot(xvalues,values,label=label,marker=m,**kwargs)

    plt.legend(loc=loc)

    f = "%s.pdf"%filename
    print "save '%s'"%f
    plt.savefig(f)

def latex_table(data, title, filename, nvalues=[5,10,15,30]):

    nl = "\\\\\n"
    hl = "\\hline"
    hln = hl+"\n" 

    alignment = "|l|" +len(nvalues)*"c|"
    column_desc = hln+"{\\bf Algorithmus}"
    for n in nvalues:
        column_desc += "& HR@%d "%n

    column_desc += nl + hl+hln

    rows_array = []
    for name, values in data:
        name = name.replace("_", "\_")
        row = "{\\bf %s} &"%name
        row += " & ".join(["%.3f"%x for x in values])

        rows_array.append(row)

    rows = (nl+hln).join(rows_array)+nl+hl
    table = column_desc + rows
    return """
\\begin{table}[h]
\\caption{%s}
\\label{tab:%s}
\\begin{tabular}{%s}
%s
\\end{tabular}
\\end{table}
    """%(title,filename,alignment,table)

if __name__=="__main__":

    params = { "title": "UserCF vs. ReductionUserCF",
            "filename": "usercf_vs_reduction",
            "data": [
                ("UserCF" , [0.0038596491228070173, 0.007192982456140351, 0.013859649122807016, 0.02184032545130943]),
                ("RedUserCF_DOW",[0.0002777777777777778, 0.007256944444444444, 0.017256944444444443, 0.035555312538652684]),
                ("RedUserCF_TOD",[0.006555555555555554, 0.0096984126984127, 0.013417050691244237, 0.0320176234397298])
                ]
            }

    plot_hrn(**params)

    params = { "title": "UserCF vs. ReductionUserCF vs. GraphCARS",
            "filename": "usercf_vs_reduction_vs_graph",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("UserCF" , [0.0038596491228070173, 0.007192982456140351, 0.013859649122807016, 0.02184032545130943]),
                ("RedUserCF_DOW",[0.0002777777777777778, 0.007256944444444444, 0.017256944444444443, 0.035555312538652684]),
                ("RedUserCF_TOD",[0.006555555555555554, 0.0096984126984127, 0.013417050691244237, 0.03201762343972987]),
                ("GraphCARS_DOW",[0.14062312573745978, 0.22376096854851973, 0.2932268347402083, 0.3873934426384362]),
                ("GraphCARS_TOD",[0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ],
            }

    plot_hrn(**params)

    params = { "title": "UserCF vs. GraphCARS",
            "filename": "graph_vs_usercf",
            "data": [
                ("UserCF" , [0.0038596491228070173, 0.007192982456140351, 0.013859649122807016, 0.02184032545130943]),
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ]
            }

    plot_hrn(**params)

    params = { "title": "GraphCARS ohne Kontext. Einfluss von Content Features",
            "filename": "graph_wo_context",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_Artists",[0.1347711581792201, 0.19737721729461946, 0.26209239470301454, 0.38100717050901217]),
                ("GraphCARS_Tags" , [0.1306978009538241, 0.21672439685030895, 0.2687175182974998, 0.3765184521038309]),
                ]
            }

    plot_hrn(**params)

    params = { "title": "GraphCARS mit Kontext. Einfluss verschiedener Kontextdimensionen",
            "filename": "graph_with_context",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_DOW",[0.14062312573745978, 0.22376096854851973, 0.2932268347402083, 0.3873934426384362]),
                ("GraphCARS_TOD",[0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ]
            }
    plot_hrn(**params)

    params = { "title": "GraphCARS mit Kontext DayOfWeek. Einfluss von Tags",
            "filename": "graph_with_dow_and_tags",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_DOW",[0.14062312573745978, 0.22376096854851973, 0.2932268347402083, 0.3873934426384362]),
                ("GraphCARS_DOW_Tags",[0.14622813928759526, 0.2341109494162032, 0.2914927186179343, 0.3865199220590332]),
                ("GraphCARS_DOW_Artist", [0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ]
            }

    plot_hrn(**params)

    params = { "title": "GraphCARS mit Kontext TimeOfDay. Einfluss von Tags",
            "filename": "graph_with_tod_and_tags",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_TOD",[0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ("GraphCARS_TOD_Tags",[0.15219919497327986, 0.22947947890101383, 0.29985239791509477, 0.38160117762031964]),
                ("GraphCARS_TOD_Artist",[0.15764346909757662, 0.21508385406838026, 0.2919854975478925, 0.3858394060597197] ),
                ]
            }
    plot_hrn(**params)

    params = { "title": "GraphCARS mit Kontext TimeOfDay vs. ShortTermPreferences",
            "filename": "graph_tod_vs_stp",
            "data": [
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_TOD",[0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ("GraphCARS_STP",[0.2554697554697555, 0.3423316173316173, 0.4128163878163878, 0.4815422565422566]),
                ("GraphCARS_STP_Tags",[0.26583011583011584, 0.3549013299013299, 0.4453238953238953, 0.5187044187044186]),
                ("GraphCARS_STP_Artist",[0.2585800085800086, 0.3755040755040755, 0.4830115830115831, 0.5197125697125696]),
                ]
            }

    plot_hrn(**params)

    params = { "title": "ShortTermPreference hr@5 for different window sizes",
            "filename": "graph_stp_windowsize",
            "xlabel": "k",
            "ylabel": r"Hit Ration bei $N=5$",
            "xvalues": [1,2,3,4,5,6,7,8,9,10],
            "data": [
                ("GraphCARS_STP",[0.16874603174603175, 0.1883095238095238, 0.17469806763285026, 0.16588224437061644, 0.17376113046844752, 0.2554697554697555, 0.17149470899470898, 0.2228174603174603, 0.18357142857142858, 0.21507936507936506]),
                ("GraphCARS_STP_Artists",[0.2432698412698413, 0.24516666666666664, 0.23840579710144924, 0.2105850867478774, 0.20807200929152148, 0.2585800085800086, 0.19212962962962962, 0.23769841269841274, 0.2397619047619048, 0.22499999999999998]),
                ("GraphCARS_STP_Tags",[0.20874603174603176, 0.21430952380952384, 0.20513285024154587, 0.19663159837578445, 0.18270421989934182, 0.26583011583011584, 0.16871693121693118, 0.23253968253968255, 0.18642857142857144, 0.22507936507936507]),
                ]
            }

    plot_hrn(**params)

    params = { "title": u"Alle Algorithmen",
            "filename": "all_algorithms",
            "data": [
                ("UserCF", [0.0038596491228070173, 0.007192982456140351, 0.013859649122807016, 0.02184032545130943]),
                ("RedUserCF_DOW",[0.0002777777777777778, 0.007256944444444444, 0.017256944444444443, 0.035555312538652684]),
                ("RedUserCF_TOD",[0.006555555555555554, 0.0096984126984127, 0.013417050691244237, 0.03201762343972987]),
                ("GraphCARS",[0.12364055680164845, 0.2134192325310601, 0.26684647118616434, 0.375252456039 ]),
                ("GraphCARS_Artists",[0.1347711581792201, 0.19737721729461946, 0.26209239470301454, 0.38100717050901217]),
                ("GraphCARS_Tags", [0.1306978009538241, 0.21672439685030895, 0.2687175182974998, 0.37651845210383095]),
                ("GraphCARS_Tags_Artists", [0.13670961327140194, 0.20138482928814525, 0.26833213323817434, 0.37619219398481263]), 
                ("GraphCARS_Tags_rel", [0.1306978009538241, 0.21700608699115398, 0.26899920843834485, 0.3760929201889373]),
                ("GraphCARS_DOW",[0.14062312573745978, 0.22376096854851973, 0.2932268347402083, 0.3873934426384362]),
                ("GraphCARS_DOW_Tags",[0.14622813928759526, 0.2341109494162032, 0.2914927186179343, 0.38651992205903324]),
                ("GraphCARS_DOW_Artist", [0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ("GraphCARS_TOD",[0.15017583714530017, 0.23194180777195608, 0.30044423358568983, 0.3766390500792447]),
                ("GraphCARS_TOD_Tags",[0.15219919497327986, 0.22947947890101383, 0.29985239791509477, 0.38160117762031964]),
                ("GraphCARS_TOD_Artist",[0.15764346909757662, 0.21508385406838026, 0.2919854975478925, 0.3858394060597197] ),
                ("GraphCARS_DOW_TOD",[0.14078548754925607, 0.2336260731157201, 0.3006786003863943, 0.3852870715040831]),
                ("GraphCARS_STP",[0.2554697554697555, 0.3423316173316173, 0.4128163878163878, 0.4815422565422566]),
                ("GraphCARS_STP_Tags",[0.26583011583011584, 0.3549013299013299, 0.4453238953238953, 0.5187044187044186]),
                ("GraphCARS_STP_Artist",[0.2585800085800086, 0.3755040755040755, 0.4830115830115831, 0.5197125697125696]),
                ],
            }

    print latex_table(**params)
