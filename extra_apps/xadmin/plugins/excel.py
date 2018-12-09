# coding:utf-8

import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from django.template.context_processors import csrf
from xadmin.plugins.utils import get_context_dict
#excel 导入
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html', get_context_dict(context)))
        # nodes.append(loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html',context=csrf(context)))


xadmin.site.register_plugin(ListImportExcelPlugin, ListAdminView)