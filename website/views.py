from flask import Blueprint, render_template,request
import matplotlib
matplotlib.use('agg')



views = Blueprint("views", __name__)

@views.route("/")

def home():
    return render_template("base.html")


@views.route("/map")
def map():
    import geopandas as gpd
    import json

    # Folder with Shapefiles
    folder_path = r'D:\Trabalho de Licenciatura\New folder\Python\Moz Geo Data\Distritos'

    # Exact shape file
    shapefile_path = folder_path + "\Distritos.shp"

    # Load shapefile dos distritos
    districts = gpd.read_file(shapefile_path)

    # Convert districts to GeoJSON
    districts_json = districts.to_crs(epsg='4326').to_json()

    return render_template("map.html", districts_json=districts_json)



@views.route("/map/district/<district_name>")
def district_page(district_name):
    import pulp 
    import openpyxl
    from flask import jsonify

    
    book= openpyxl.load_workbook(r"D:\Trabalho de Licenciatura\New folder\Python\WebApp\website\static\Dados_py.xlsx")
    worksheet=book["Dados"]
    
    for row in worksheet.iter_rows(min_row=1, values_only=True):
        if row[0]==district_name:
            Irr=str(row[1])
            Temp=str(row[2])
            Vent=str(row[3])

    Irr=float(Irr)
    Temp=float(Temp)
    Vent=float(Vent)
    
    return render_template("district.html", district_name=district_name,Temp=Temp,Irr=Irr,Vent=Vent)


@views.route("/map/district/<district_name>/calculate", methods=["POST"])
def calculate(district_name):
    import pulp 
    import openpyxl
    from flask import jsonify
    import matplotlib.pyplot as plt
    import numpy as np
    import mpl_toolkits.mplot3d as Axes3D
    import math
    demand = float(request.form["demand"])
    PF = float(request.form["pf"])
    PE= float(request.form["pe"])
    book = openpyxl.load_workbook(r"D:\Trabalho de Licenciatura\New folder\Python\WebApp\website\static\Dados_py.xlsx")
    worksheet = book["Dados"]
    
    for row in worksheet.iter_rows(min_row=1, values_only=True):
        if row[0] == district_name:
            G = float(row[1])
            T = float(row[2])
            V = float(row[3])
            Q = float(row[4])
    
    
    PM = float(PF*G/1000*(1+0.0006*(T-25)))
    PT = round(0.9561*math.exp(-((V-25.5731)/(8.2016))**2)+0.5874*math.exp(-((V-11.0979)/(4.1853))**2)+0.6075*math.exp(-((V-16.3506)/(5.4920))**2),4)
    print (PM)
    print(PT)
    model = pulp.LpProblem(name="Lp", sense=pulp.const.LpMinimize)

    x_1 = pulp.LpVariable(name="Solar", lowBound=0, cat= 'Integer')
    x_2 = pulp.LpVariable(name="Eólica", lowBound=0, cat="Integer")
    x_3 = pulp.LpVariable(name="Hídrica", lowBound=0)
    
    obj_func =4647*x_1*PF+8802*x_2*PE+8545*Q*x_3
    
    model += obj_func
    
    model += (8670*x_1*PM+8670*x_2*PT*PE+17218.7*Q*x_3 >= demand*10**6)
    model += (8670*x_2*PT*PE<= 0.3*demand*10**6)
    model += (8670*x_1*PM<= 0.80*demand*10**6)
    model += (x_3<= 25)
    model += (17218.7*Q*x_3<= 0.1*demand*10**6)
    model += (17218.7*Q*x_3<=8670*x_2*PT*PE )

    
    
    results_dict = {}
    status = model.solve()
    for var in model.variables():
        results_dict[var.name] = var.value()
    
    x_1_value = results_dict["Solar"]
    x_2_value = results_dict["Eólica"]
    x_3_value = results_dict["Hídrica"]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = np.linspace(0, demand, 50)
    y = np.linspace(0, demand, 50)
    X, Y = np.meshgrid(x, y)

    Z1 = (demand*10**6 - 8670*Y*PM - 8670*X*PT*PE)/(17218.7*Q)
    # Plotting the feasible region
    ax.scatter(x_1_value, x_2_value, x_3_value, color='red', label='Optimal Solution')    
    ax.plot_surface(X, Y, Z1, alpha=1, color='blue', label=f'Demanda Energetica')

    
    ax.set_xlabel("Módulos fotovoltaicos")
    ax.set_ylabel("Turbinas Eólicas")
    ax.set_zlabel("Altura do subsistema hídrico")

    # Manually specify legend handles and labels
    legend_handles = [plt.Rectangle((0, 0), 1, 1, fc='blue', alpha=0.5),
                      plt.Line2D([0], [0], marker='o', color='red', label='Solução óptima')]
    legend_labels = [f'$x_1$ + $x_2$ + $x_3$ = {demand}',
                     f'41$x_1$+11$x_2$+24$x_3$ = 20*{demand}',f'$x_3$=0.399$x_1$ ',f'$x_3$=0.309$x_2$ ',
                     'Solução óptima']

    # Add legend with adjusted properties
    ax.legend(handles=legend_handles, labels=legend_labels, loc='upper left',
              bbox_to_anchor=(0.05, 0.99), ncol=2, prop={'size': 7})
    
    # Save the plot image to a file
    plot_image = 'D:\\Trabalho de Licenciatura\\New folder\\Python\\WebApp\\website\\static\\images\\plot.png'
    plt.savefig(plot_image)

    # Close the figure to free up resources
    plt.close()

    # Pass the image path as a variable to the template
    return jsonify(results_dict=results_dict, plot_image=plot_image)
