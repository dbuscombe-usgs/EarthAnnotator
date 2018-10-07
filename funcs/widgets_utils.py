## written by Dr Daniel Buscombe
## Northern Arizona University
## daniel.buscombe@nau.edu


from ipywidgets import widgets
import matplotlib as mpl
global labels_widget

# =========================================================	
def create_colorpicker():

    # =========================================================
    def make_colorpicker(color):
        return widgets.ColorPicker(
            concise=False,
            description='Pick a color',
            value=color,
            disabled=False
        )
	
    # =========================================================	
    def make_label(label):
        return widgets.Text(
            value=label,
            placeholder='Type something',
            description='Class:',
            disabled=False
        )

    # =========================================================
    def save_one(b):
        label_fname = files_widget.children[0].value
        color_fname = files_widget.children[1].value

        label_f = open(label_fname, 'w')
        color_f = open(color_fname, 'w')

        labels = [item.children[0].value for item in labels_widget.children[:]]
        colors = [item.children[1].value for item in labels_widget.children[:]]

        label_f.write('\n'.join(labels))
        color_f.write('\n'.join(colors))

        label_f.close()
        color_f.close()

    # =========================================================
    def add_one(b):
        new_label = make_label('new class...')
        new_color = make_colorpicker('red') 
        new_item = widgets.HBox([new_label, new_color])

        labels_widget.children += (new_item, ) 

    # =========================================================	
    def del_last(b):
        labels_widget.children = (*labels_widget.children[:-1], ) 

    # =========================================================	
    def load(b):
        labels_widget.children = (*labels_widget.children[:-1], ) 


    cc = mpl.colors.ColorConverter()

    labels = ['class1', 'class2', 'class3']
    colors = ['b', 'r', 'y']

    items = []
    for label, color in zip(labels, colors):
        label_text = make_label(label)
        color_picker = make_colorpicker(mpl.colors.to_hex(cc.to_rgb(color)))
        item = widgets.HBox([label_text, color_picker])
        items.append(item)
    
    #save_btn = widgets.Button(
    #    description='Save to Files',
    #    disabled=False,
    #    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
    #    tooltip='Description',
    #    icon='save'
    #)
                 
    #save_btn.on_click(save_one)

    add_btn = widgets.Button(
        description='Add Class',
        disabled=False,
        button_style='info', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Description',
        icon='plus'
    )
        
    add_btn.on_click(add_one)

    del_btn = widgets.Button(
        description='Remove Last Class',
        disabled=False,
        button_style='danger', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Description',
        icon='minus'
    )

    del_btn.on_click(del_last)

    load_btn = widgets.Button(
        description='Load From File',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Description',
        icon=''
    )
    
    load_btn.on_click(del_last)
    labels_widget = widgets.VBox(items)
    controls = widgets.HBox([add_btn, del_btn]) #save_btn
    return widgets.VBox([labels_widget, controls]), labels_widget

	