from win11toast import toast
import webbrowser

def open_markets_corr(toast_args):
    argument = toast_args.get('arguments')
    print(argument)
    if argument == 'http:Dismiss':
        return
    elif argument == 'http:Open':
        webbrowser.open_new("C:\\Users\\User\\Desktop\\projects\\trading\\apps\\markets_corr.html")

toast('test2', on_click=lambda args: open_markets_corr(args), buttons=['Open', 'Dismiss'])