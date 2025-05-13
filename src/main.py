import json
import argparse
import violin

def load_instruments(file="data/instruments.json"):
    instruments = None
    with open(file, "r") as jsonfile:
        jsonstr = jsonfile.read()
        instruments = json.loads(jsonstr)
    return instruments

def save_instruments(instruments, file="data/instruments.json", indent=None):
    if instruments is None:
        return 1
    with open(file, "w") as jsonfile:
        jsonfile.write(json.dumps(instruments, indent=indent))

    return 0


def main(args):
    data = load_instruments()
    save_instruments(data, indent=4)


    selection = data[args.instrument] if args.instrument and args.instrument.casefold() in [x.casefold() for x in data.keys()] else data
    selection = selection[args.maker] if selection and args.maker and args.maker.casefold() in [x.casefold() for x in selection.keys()] else selection
    
    if args.model:
        fltr = lambda x: args.model.casefold() in x['name'].casefold() or str(x['year']) in args.model
        selection = [x for x in filter(fltr, selection)]

    if (args.model is not None) and len(selection) == 1:
        
        if 'km' in selection[0]:
            kmu = selection[0]['km']
            kml = selection[0]['km']
        else:
            kmu = selection[0]['kmu']
            kml = selection[0]['kml']

        instrument = violin.Violin(
            h=selection[0]['h'],
            kc=selection[0]['kc'],
            ku=selection[0]['ku'],
            kmu=kmu,
            kml=kml,
            kw=selection[0]['kw'],
            b1=selection[0]['b1'],
            b2=selection[0]['b2'],
            bu=selection[0]['bu'],
            bl=selection[0]['bl'],
            cu1=selection[0]['cu1'],
            cu2=selection[0]['cu2'],
            cl1=selection[0]['cl1'],
            cl2=selection[0]['cl2']
        )
        instrument.calculate_body_params()
        instrument.calculate_corner_params()
        
        height, width = instrument.get_dimensions()
        svgstr = f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\">\n"
        svgstr += instrument.get_outline_path(color="white") + "\n"
        svgstr += instrument.get_circles_svg()
        if "af" in selection[0]:
            afc = selection[0]['afc'] if 'afc' in selection[0] else None
            afd = selection[0]['afd'] if 'afd' in selection[0] else None
            svgstr += instrument.get_arches_path_on_outline(selection[0]["af"], afc=afc, afd=afd)
            svgstr += "\n"
        if "ab" in selection[0]:
            svgstr += instrument.get_arches_path_on_outline(-selection[0]["ab"], color="yellow", long_color="cyan")
            svgstr += "\n"
        svgstr += "</svg>\n"
        with open("out.svg", "w") as fout:
            fout.write(svgstr)
        
        print(instrument.get_dimensions_mm())


    else:
        if args.maker is not None:
            for i in selection:
                print(f"{i['name']} {i['year']}")
        else:
            for i in selection.keys():
                print(i)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='FourCircle'
    )

    parser.add_argument('instrument', nargs='?')
    parser.add_argument('maker', nargs='?')
    parser.add_argument('model', nargs='?')
    parser.add_argument('-a', '--all', action='store_true')  # on/off flag
    parser.add_argument('-v', '--dbg', action='store_true')  # on/off flag
    main(parser.parse_args())