#!/usr/bin/python
# coding: utf-8
#+--------------------------------------------------------------------
#|   宝塔第三方软件商店插件
#+--------------------------------------------------------------------
import sys,os,json,requests,time,base64,shutil

#设置运行目录
os.chdir("/www/server/panel")
#!/usr/bin/python
# coding: utf-8
#+--------------------------------------------------------------------
#|   宝塔第三方软件商店插件
#+--------------------------------------------------------------------
import sys,os,json,requests,time,base64,shutil

#设置运行目录
os.chdir("/www/server/panel")

#添加包引用位置并引用公共包
sys.path.append("class/")
import public
from panelPlugin import panelPlugin

class three_soft_main:
    __plugin_path = "/www/server/panel/plugin/three_soft/"
    __config = None
    __tmp_path = '/tmp/plugins'
    __list_url = ""
    __list_path = __plugin_path + "plugin.json"
    __config_path = __plugin_path + "config.json"

    #构造方法
    def  __init__(self):
        #config =  json.loads(public.readFile(self.__config_path))
        #self.__list_url = config['home'] + "/script/three_soft/config/get_soft_list.json"
        self.__list_url = "https://raw.githubusercontent.com/gacjie/btpanel_three_soft/main/plugin.json"
        pass

    #从获取插件列表
    def get_soft_list(self, args):
        if not os.path.exists(self.__list_path) or (time.time() - os.stat(self.__list_path).st_mtime) > 86400:
            self.update_soft_list(args);
        data =  json.loads(public.readFile(self.__list_path))
        for i in data:
            soft_path = '/www/server/panel/plugin/'+i['name']+'/info.json'
            i['exists'] = os.path.exists(soft_path)
            i['local_version'] = i['version']
            if i['exists']:
                info = json.loads(public.readFile(soft_path))
                i['local_version'] = info['versions']
        return self.__response_json(data)
        
    #更新插件列表
    def update_soft_list(self, args):
        try:
            res = public.HttpGet(self.__list_url).encode()
            try:
                json.loads(res)
                public.writeFile(self.__list_path,res,"wb")
            except:pass
        except:
            return self.__response_json('',500,'列表更新失败')
        return self.__response_json('',200,'列表更新成功')
        
    #安装插件
    def install_soft(self, args):
        print('')
        tmp_path = '/www/server/panel/temp'
        if not os.path.exists(tmp_path): os.makedirs(tmp_path,mode=384)
        public.ExecShell("rm -rf " + tmp_path + '/*')
        tmp_file = tmp_path + '/' + args.name + '.zip'
        public.downloadFile(args.download,tmp_file)
        import panelTask
        panelTask.bt_task()._unzip(tmp_file,tmp_path,'','/dev/null')
        os.remove(tmp_file)
        p_info = tmp_path + '/info.json'
        if not os.path.exists(p_info):
            d_path = None
            for df in os.walk(tmp_path):
                if len(df[2]) < 3: continue
                if not 'info.json' in df[2]: continue
                if not 'install.sh' in df[2]: continue
                if not os.path.exists(df[0] + '/info.json'): continue
                d_path = df[0]
            if d_path:
                tmp_path = d_path
                p_info = tmp_path + '/info.json'
        if not os.path.exists(tmp_path): return public.returnMsg(False,'临时文件不存在,请重新上传!')
        plugin_path = '/www/server/panel/plugin/' + args.name
        if not os.path.exists(plugin_path): os.makedirs(plugin_path)
        public.ExecShell("\cp -a -r " + tmp_path + '/* ' + plugin_path + '/')
        public.ExecShell('chmod -R 600 ' + plugin_path)
        filename = plugin_path + '/install.sh'
        if not os.path.exists(filename): return False
        env_py = '/www/server/panel/pyenv/bin'
        if not os.path.exists(env_py): return False
        temp_file = public.readFile(filename)
        env_path=['PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin']
        rep_path=['PATH={}/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin'.format(env_py+":")]
        for index_key in range(len(env_path)):
            temp_file = temp_file.replace(env_path[index_key],rep_path[index_key])
        public.writeFile(filename,temp_file)
        public.ExecShell('cd ' + plugin_path + ' && bash install.sh install &> /tmp/panelShell.pl')
        p_info = public.ReadFile(plugin_path + '/info.json')
        public.ExecShell("rm -rf /www/server/panel/temp/*")
        if p_info:
            #----- 增加图标复制 hwliang<2021-03-23> -----#
            icon_sfile = plugin_path + '/icon.png'
            icon_dfile = '/www/server/panel/BTPanel/static/img/soft_ico/ico-{}.png'.format(args.name)
            if os.path.exists(plugin_path + '/icon.png'):
                import shutil
                shutil.copyfile(icon_sfile,icon_dfile)
            #----- 增加图标复制 END -----#
            public.WriteLog('软件管理','安装第三方插件[%s]' % json.loads(p_info)['title'])
            install_pl = '/www/server/panel/plugin/'+args.name+'/install.pl'
            public.writeFile(install_pl,'')
            return public.returnMsg(True,'安装成功!')
        public.ExecShell("rm -rf " + plugin_path)
        return public.returnMsg(False,'安装失败!')
        
    def get_install_status(self, args):
        install_pl = '/www/server/panel/plugin/'+args.name+'/install.pl'
        if os.path.exists(install_pl):
            return self.__response_json({'status':1},200,'插件安装成功')
        return self.__response_json({'status':0},500,'插件安装失败')
        
    def __response_json(self, data, code=0, msg=''):
        response = {"code": code, "msg": msg, "data": data}
        return response
