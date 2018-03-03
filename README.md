# zabbix_nginx_vts
Скрипты мониторинга zabbix для nginx-module-vts

<b>Требования</b>


<a href="https://nginx.org/ru/">nginx</a> и установленный модуль <a href="https://github.com/vozlt/nginx-module-vts">#nginx-module-vts</a> 



Скрипты переделаны из скриптов для NGINX PLUS <a href="https://github.com/strannick-ru/nginx-plus-zabbix">nginx-plus-zabbix</a>, что-то добавлено, что-то сломано))

<b>Установка</b>

Добавить в 

/etc/zabbix/zabbix_agentd.d/userparameter_nginx_vts.conf



<code>
UserParameter=nginx.stat.[*],/etc/zabbix/scripts/nginx-stats.py $1 $2 $3 $4 $5 $6 $7
UserParameter=nginx.discovery[*],/etc/zabbix/scripts/nginx-discovery.py $1
</code>


перезапустить zabbix-agent

импортировать шаблон Zabbix

присоединить шаблон Nginx VTS к узлу сети

проверить наличие свежих данных


<img src="https://github.com/Vovanys/zabbix_nginx_vts/blob/master/img/lastdata.jpg?raw=true">