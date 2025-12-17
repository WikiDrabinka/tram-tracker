import folium

def repr_tram(tram: dict[str, str]) -> str:
    return f"Number: {tram["id"]}\nRoute: {tram["routeId"]}\nDelay: {tram["delay"]}s\nModel: {tram["type"]}"

def map_trams(trams: list[dict[str,str]]) -> folium.Map:

    map = folium.Map()
    map.fit_bounds([[52.36,16.85],[52.46,17]])

    for tram in trams:
        b_color = "#ddd" if type(tram["currentStatus"]) == str else "#2ad"
        f_color = "#444" if type(tram["currentStatus"]) == str else "#eee"
        style = f"background-color:{b_color};width:20px;height:20px;color:{f_color};border:1px solid {f_color};border-radius:10px;font-weight:bold; display:flex;justify-content:center;align-items:center;"
        folium.Marker(location=[tram["latitude"], tram["longitude"]], tooltip=repr_tram(tram), icon=folium.DivIcon(f'<p style="{style}">{int(tram["routeId"])}</p>')).add_to(map)

    return map