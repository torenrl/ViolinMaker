import json
import argparse
import violin
from svg import Svg

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
    # json cleanup each time :)
    data = load_instruments()
    save_instruments(data, indent=4)

    #TODO: make this case insensitive
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

        transpose = [0,0]
        image = ""
        if args.image:
            transpose = [5,5]
            width += 2*transpose[0]*Svg._px2mm
            height += 2*transpose[1]*Svg._px2mm

            image_size = height
            if args.image_resize:
                image_size *= args.image_resize
            image_dx = (width-image_size)/2
            if args.image_dx:
                image_dx += Svg._px2mm*args.image_dx
            image_dy = -args.image_dy if args.image_dy else 0

            image = f"<image href=\"{args.image}\" width=\"{image_size}\" height=\"{image_size}\" x=\"{image_dx}\" y=\"{image_dy}\"/> \n" 

        svgstr = f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\">\n"
        svgstr += image

        color = args.color if args.color else "black"

        if args.template:
            svgstr += instrument.get_template(color=color, move=transpose, type=args.instrument) + "\n"
        else:
            svgstr += instrument.get_outline_path(color=color, move=transpose) + "\n"
            if "af" in selection[0]:
                afc = selection[0]['afc'] if 'afc' in selection[0] else None
                afd = selection[0]['afd'] if 'afd' in selection[0] else None
                svgstr += instrument.get_arches_path_on_outline(selection[0]["af"], afc=afc, afd=afd, move=transpose)
                svgstr += "\n"
            if "ab" in selection[0]:
                svgstr += instrument.get_arches_path_on_outline(-selection[0]["ab"], color="yellow", long_color="cyan", move=transpose)
                svgstr += "\n"

        if args.circles:
            svgstr += instrument.get_circles_svg(move=transpose)
        
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
    parser.add_argument('-t', '--template', action='store_true')
    parser.add_argument('-c','--circles', action='store_true')
    parser.add_argument('-i', '--image', type=str)
    parser.add_argument('--color', type=str)
    parser.add_argument('--image_dx', type=float)
    parser.add_argument('--image_dy', type=float)
    parser.add_argument('--image_resize', type=float)
    main(parser.parse_args())