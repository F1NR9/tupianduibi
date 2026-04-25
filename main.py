from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
import tempfile
from feature_extractor import FeatureExtractor
from matcher import Matcher

class JerseyMatcherApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.matcher = Matcher()
        self.extractor = FeatureExtractor()
        # 确保数据目录存在
        self.image_dir = os.path.join(os.getcwd(), 'data', 'images')
        os.makedirs(self.image_dir, exist_ok=True)
        # 构建索引
        self.matcher.build_index(self.image_dir)
    
    def build(self):
        # 设置窗口大小
        Window.size = (360, 640)
        
        # 创建主布局
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 添加标题
        title = Label(text='球衣款式匹配系统', font_size='24sp', halign='center')
        layout.add_widget(title)
        
        # 添加状态标签
        self.status_label = Label(text='系统已就绪', halign='center', size_hint_y=0.1)
        layout.add_widget(self.status_label)
        
        # 添加上传按钮
        upload_btn = Button(text='选择图片', size_hint_y=0.15)
        upload_btn.bind(on_release=self.show_file_chooser)
        layout.add_widget(upload_btn)
        
        # 添加匹配结果区域
        scroll_view = ScrollView(size_hint_y=0.6)
        self.results_layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        scroll_view.add_widget(self.results_layout)
        layout.add_widget(scroll_view)
        
        return layout
    
    def show_file_chooser(self, instance):
        # 打开文件选择器
        filechooser = FileChooserListView()
        filechooser.bind(on_submit=self.on_file_selected)
        self.root.add_widget(filechooser)
    
    def on_file_selected(self, filechooser, selection, touch):
        if selection:
            image_path = selection[0]
            self.root.remove_widget(filechooser)
            self.process_image(image_path)
    
    def process_image(self, image_path):
        # 显示加载状态
        self.status_label.text = '正在处理图片...'
        
        # 匹配图片
        results = self.matcher.match(image_path, top_k=5)
        
        # 显示结果
        self.results_layout.clear_widgets()
        
        if results:
            for result in results:
                # 创建结果项
                result_item = BoxLayout(orientation='vertical', padding=5, spacing=5, size_hint_y=None, height=200)
                
                # 显示图片
                try:
                    img = Image(source=result['image_path'], size_hint_y=0.7)
                    result_item.add_widget(img)
                except Exception as e:
                    error_label = Label(text='无法加载图片', halign='center', size_hint_y=0.7)
                    result_item.add_widget(error_label)
                
                # 显示相似度
                distance = result['distance']
                similarity = (1 - distance) * 100
                similarity_label = Label(text=f'相似度: {similarity:.2f}%', halign='center', size_hint_y=0.15)
                result_item.add_widget(similarity_label)
                
                # 显示图片名称
                image_name = os.path.basename(result['image_path'])
                name_label = Label(text=image_name, halign='center', font_size='12sp', size_hint_y=0.15)
                result_item.add_widget(name_label)
                
                self.results_layout.add_widget(result_item)
        else:
            no_result_label = Label(text='未找到匹配结果', halign='center', size_hint_y=0.5)
            self.results_layout.add_widget(no_result_label)
        
        # 更新状态
        self.status_label.text = '处理完成'

if __name__ == '__main__':
    JerseyMatcherApp().run()
