import json
##Minizinc
from logging import exception, root
from minizinc import Instance, Model, Solver, model
##Interfaz
import tkinter as tk
from tkinter import * 
from tkinter import ttk  
from tkinter.filedialog import askopenfilename


def conectMinizinc(file): 
    # Load  model from file
    project = Model("../proyectoPR.mzn")
    # Find the MiniZinc solver configuration 
    ##Para hacerlo con Gecode, cambiar chuffed por gecode
    solver = Solver.lookup("chuffed")
    # Create an Instance of the project model for solver
    instance = Instance(solver, project)
    # Assign the values from a dzn
    instance.add_file(file)
    result = instance.solve()
    # Output
    #print([result["docks"],result["arrivalTime"],result["unloadStartTime"]])
    texto = str(result)
    texto = texto.replace("'",'"')
    mijson = json.loads(texto)
    mijson['ClimaBarco']=arreglo1d_2d(mijson['ClimaBarco'])
    mijson['MareaBarco']=arreglo1d_2d(mijson['MareaBarco'])
    mijson['HoraLlegadas']=arreglo1d_2d2(mijson['HoraLlegadas'])
    mijson['HorasHabil']=arreglo1d_2d2(mijson['HorasHabil'])
    return ([result["docks"],result["arrivalTime"],result["unloadStartTime"],mijson])

def arreglo1d_2d(arr):
    it = 0
    auxp = []
    while it < len(arr):
        aux = []
        aux.append(arr[it])
        aux.append(arr[it+1])
        aux.append(arr[it+2])
        auxp.append(aux)
        it+=3
    return auxp

def arreglo1d_2d2(arr):
    it = 0
    auxp = []
    while it < len(arr):
        aux = []
        aux.append(arr[it])
        aux.append(arr[it+1])
        auxp.append(aux)
        it+=2
    return auxp

##Funciones
def verifications(condition,frame,posx,posy):
    if condition == 1:
        lc = tk.Label(frame, bg ='white', text='✓',fg = 'black', font =("Courier", 20))
        lc.pack()
        lc.place(x=posx,y=posy,height=30, width=12)
    else:
        lc = tk.Label(frame,bg ='white', text='✗',fg = 'black',font =("Courier", 20))
        lc.pack()
        lc.place(x=posx,y=posy,height=30, width=12)
    return lc
fileName = ""
def selectFile():
    global fileName
    Tk().withdraw() 
    fileName = askopenfilename()
    #print("fN",fileName)
    try:
        result = conectMinizinc(fileName)
    except Exception as e :
        result = [[0],[0],[0]]
    drawSolution(result)
    return result

def drawSolution(resultData):

    if resultData == [[0],[0],[0]]:
        lb = Label(sFrame, bg = 'beige', fg = 'black', font =("Courier", 18), height = 3, width = 52, 
        text = "NO HAY SOLUCIÓN").pack()
    else:
        ##Asignacion variables
        shipsID = resultData[3]['Barcos']
        docksID = resultData[3]['Muelles']
        shipsWaitTime = resultData[3]['TiempoEspera']
        shipsWeather = resultData[3]['ClimaBarco']
        dryWeather = []
        humidWeather = []
        rainyWeather = []
        for sw in shipsWeather:
            dryWeather.append(sw[0])
            humidWeather.append(sw[1])
            rainyWeather.append(sw[2])

        shipsUnloadTime = resultData[3]['TiempoDesca']
        shipsTideState = resultData[3]['MareaBarco']
        lowTide = []
        midTide = []
        highTide = []
        for st in shipsTideState:
            lowTide.append(st[0])
            midTide.append(st[1])
            highTide.append(st[2])

        P_estadost = resultData[3]['Clima']
        P_estadosm = resultData[3]['Marea']
        horaLlegada= resultData[3]['HoraLlegadas']
        workingHours = resultData[3]['HorasHabil']

        for idx,fm in enumerate(resultData[0]):
            hours = 'No especificada'
            for h in horaLlegada:
                if(h[0]) == idx+1:
                    hours = str(h[1])
            avalaible = ''
            for i,av in enumerate(docksID):
                if fm == av:
                    avalaible = 'desde '+ str(workingHours[i][0])+ ' hasta '+str(workingHours[i][1])

            solutionWeather = P_estadost[resultData[1][idx]-1:resultData[2][idx]+shipsUnloadTime[idx]-1]
            #print(solutionWeather)
            solutionTide = P_estadosm[resultData[1][idx]-1:resultData[2][idx]+shipsUnloadTime[idx]-1]
            #print(solutionTide)

            frame = tk.Frame(sFrame, bg ='white', height=350, width=620, bd= 1,relief ="solid")
            frame.pack(fill=None,expand=1)
            frame.place(x=30, y=230+(350*idx))
            l1 = tk.Label(frame,image=ship, bg ='white', fg = 'black', font =("Courier", 20),compound=tk.LEFT, bd= 1,
            text='BARCO N° '+ str(shipsID[idx]))
            l1.pack()
            l1.place(x=200,y=0, height=30, width=220)
            l2 = tk.Label(frame, bg ='white', fg = 'black', font =("Courier", 20),compound=tk.LEFT, bd= 1,
            text='CONDICIONES CLIMÁTICAS')
            l2.pack()
            l2.place(x=0,y=50,height=30, width=618)
            l3 = tk.Label(frame,image=dry, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Seco' )
            l3.pack()
            l3.place(x=85,y=100,height=30, width=90)
            verifications(dryWeather[idx],frame,175,100)
            l4 = tk.Label(frame,image=humid, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Humedo')
            l4.pack()
            l4.place(x=205,y=100,height=30, width=120)
            verifications(humidWeather[idx],frame,325,100)
            l5 = tk.Label(frame,image=rainy, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Lluvioso')
            l5.pack()
            l5.place(x=355,y=100,height=30, width=150)
            verifications(rainyWeather[idx],frame,505,100)
            l6 = tk.Label(frame, bg ='white', fg = 'black', font =("Courier", 20),compound=tk.LEFT, bd= 1,
            text='CONDICIONES DE LA MAREA')
            l6.pack()
            l6.place(x=0,y=150,height=30, width=618)
            l7 = tk.Label(frame,image=low, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Baja' )
            l7.pack()
            l7.place(x=115,y=200,height=30,width=95)
            verifications(lowTide[idx],frame,210,200)
            l8 = tk.Label(frame,image=mid, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Media' )
            l8.pack()
            l8.place(x=240,y=200,height=30,width=110)
            verifications(midTide[idx],frame,350,200)
            l9 = tk.Label(frame,image=high, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Alta' )
            l9.pack()
            l9.place(x=380,y=200,height=30,width=95)
            verifications(highTide[idx],frame,475,200)
            l20 = tk.Label(frame,image=time, bg ='white', fg = 'black', font =("Courier", 18),compound=tk.LEFT, bd= 1,
            text='Hora de llegada: '+hours)
            l20.pack()
            l20.place(x=0,y=250,height=30,width=575)
            l21 = tk.Label(frame,image=ava, bg ='white', fg = 'black', font =("Courier", 18),compound=tk.LEFT, bd= 1,
            text='Muelle habilitado '+avalaible)
            l21.pack()
            l21.place(x=0,y=300,height=30,width=618)
            
            frame1 = tk.Frame(sFrame, bg ='white', height=350, width=790, bd= 1,relief ="solid")
            frame1.pack(fill=None,expand=1)
            frame1.place(x=650, y=230+(350*idx))
            
            l12 = tk.Label(frame1,image=dock, bg ='white', fg = 'black', font =("Courier", 20),compound=tk.LEFT, bd= 1,
            text='MUELLE N° '+ str(fm))
            l12.pack()
            l12.place(x=185,y=0,height=30, width=240)
            l10 = tk.Label(frame1,image=wait, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Tiempo de espera:'+ str(shipsWaitTime[idx]))
            l10.pack()
            l10.place(x=0,y=50,height=30,width=290)
            l11 = tk.Label(frame1,image=unload, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Tiempo de descarga:'+ str(shipsUnloadTime[idx]))
            l11.pack()
            l11.place(x=290,y=50,height=30,width=310)
            l13 = tk.Label(frame1,image=arrival, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Llegada:'+ str(resultData[1][idx]))
            l13.pack()
            l13.place(x=10,y=100,height=30, width=180)
            l14 = tk.Label(frame1,image=startD, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Descarga:'+ str(resultData[2][idx]))
            l14.pack()
            l14.place(x=200,y=100,height=30, width=200)
            l15 = tk.Label(frame1,image=finish, bg ='white', fg = 'black', font =("Courier", 16),compound=tk.LEFT, bd= 1,
            text='Finaliza:'+ str(resultData[2][idx]+shipsUnloadTime[idx]-1))
            l15.pack()
            l15.place(x=410,y=100,height=30, width=200)
            l16 = tk.Label(frame1,image=time, bg ='#b2ffff', bd= 1,relief ="solid")
            l16.pack()
            l16.place(x=10,y=150,height=50, width=50)
            l17 = tk.Label(frame1,image=weather, bg ='#b2ffff', bd= 1,relief ="solid")
            l17.pack()
            l17.place(x=10,y=200,height=50, width=50)
            l18 = tk.Label(frame1,image=mid, bg ='#b2ffff', bd= 1,relief ="solid")
            l18.pack()
            l18.place(x=10,y=250,height=50, width=50)
            for i,sol in enumerate(solutionWeather):
                if sol==1:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='S')
                elif sol==2:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='H')
                else:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='L')                    
                la.pack()
                la.place(x=10+((i+1)*50),y=200,height=50, width=50)
                la1 = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text=str(i+resultData[1][idx]))
                la1.pack()
                la1.place(x=10+((i+1)*50),y=150,height=50, width=50)

            for i,sol in enumerate(solutionTide):
                if sol==4:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='B')
                elif sol==5:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='M')
                else:
                    la = tk.Label(frame1,bg ='#b2ffff', fg = 'black', font =("Courier", 12), bd= 1,relief ="solid",
                    text='A')                    
                la.pack()
                la.place(x=10+((i+1)*50),y=250,height=50, width=50)

##Interfaz
root = Tk()
root.geometry('1300x1300')
root.configure(bg = 'beige')
root.title('Proyecto')

mainFrame = tk.Frame(root)
mainFrame.pack(fill=BOTH,expand=1)

canvas = tk.Canvas(mainFrame)
canvas.pack(side=LEFT,fill=BOTH,expand=1)

scrollBar = tk.Scrollbar(mainFrame,orient=VERTICAL, command=canvas.yview)
scrollBar.pack(side=RIGHT,fill=Y)

canvas.configure(yscrollcommand=scrollBar.set)
#canvas.configure(xscrollcommand=scrollBar.set)
canvas.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

sFrame = tk.Frame(canvas,  bg= 'beige')
canvas.create_window((0,0),window=sFrame,anchor="nw",height=8000,width=1450)

scrollBarx = tk.Scrollbar(canvas, orient='horizontal',command=canvas.xview)
scrollBarx.pack(side=TOP,fill=X)
canvas.configure(xscrollcommand=scrollBarx.set)

ship = tk.PhotoImage(file="ship.png")
dock = tk.PhotoImage(file="dock.png")
weather = tk.PhotoImage(file="weather.png")
dry = tk.PhotoImage(file="dry.png")
humid = tk.PhotoImage(file="humid.png")
rainy = tk.PhotoImage(file="rainy.png")
low = tk.PhotoImage(file="low.png")
mid = tk.PhotoImage(file="mid.png")
high = tk.PhotoImage(file="high.png")
unload = tk.PhotoImage(file="unload.png")
wait = tk.PhotoImage(file="wait.png")
time = tk.PhotoImage(file="time.png")
arrival = tk.PhotoImage(file="arrival.png")
startD = tk.PhotoImage(file="startD.png")
finish = tk.PhotoImage(file="finish.png")
ava = tk.PhotoImage(file="available.png")


l1 = Label(sFrame, bg = 'beige', fg = 'black', font =("Courier", 18), height = 3, width = 52, 
text = "Planificación automática de horas de descargue \n para un puerto naval comercial").pack()
l2= Label(sFrame, bg = 'beige', fg = 'black', font =("Courier", 12), height = 3, width = 80, justify=LEFT,
text = "Para comenzar, seleccione el archivo .dzn con la información del puerto").pack()


boton = ttk.Button(sFrame,text="Seleccionar archivo", command= selectFile)
boton.place(x=350, y=9)
boton.pack(pady=10)


ttk.Button(sFrame, text='Salir', command=quit).pack(pady=10,side=TOP)
root.mainloop()
