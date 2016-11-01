# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Parser de http://www.arenavision.me by DMax
# Version 0.1 (03.08.2016)
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------

import os
import sys
import urllib
import urllib2
import re

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import time

import plugintools, requests
from resources.tools.resolvers import *
from resources.tools.media_analyzer import *
from __main__ import *
#from datetime import datetime
import datetime, locale
from datetime import datetime, timedelta



playlists = xbmc.translatePath(os.path.join('special://userdata/playlists', ''))
temp = xbmc.translatePath(os.path.join('special://userdata/playlists/tmp', ''))

addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")

thumbnail = 'http://i.imgur.com/IdjjIKU.png'
fanart = 'http://i52.fastpic.ru/big/2013/0411/4f/90ba9f4496ac42468023d639c407884f.jpg'

url = 'http://arenavision.in'
url_ref = 'http://arenavision.in/'
url_agenda = 'http://arenavision.in/agenda'

dicdias={'Monday':'Lunes','Tuesday':'Martes','Wednesday':'Miercoles','Thursday':'Jueves','Friday':'Viernes','Saturday':'Sabado','Sunday':'Domingo'}

version = "(v0.03)"

fich_hora = xbmc.translatePath(os.path.join('special://userdata/playlists/horario.txt'))
def arena_dmax0(params):
	plugintools.log("[%s %s] http://arenavision.in/agenda %s " % (addonName, addonVersion, repr(params)))

	r = requests.get(url_agenda)	
	data = r.content

	plugintools.add_item(action="",url="",title="[COLOR blue][B]                 ArenaVision[/B]   [I]"+version+"[/I][/COLOR][COLOR yellow][I]    **** byDarioMO ****[/I][/COLOR]",thumbnail="http://s15.postimg.org/bicwnygez/ARENAVISION.jpg",fanart=fanart,folder=False,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail="http://static.wixstatic.com/media/41d000_0ba0b768e7c98113d7fb91b13075748d.png_srz_980_236_85_22_0.50_1.20_0.00_png_srz", fanart=fanart, folder=False, isPlayable=False)

	periodo_agenda = plugintools.find_single_match(data,'Schedule(.*?)<')
	periodo_agenda = "[COLOR red][I]Agenda: " + periodo_agenda.strip().upper().replace("FROM","Desde el  ").replace("TO","  a el  ") + "[/I][/COLOR]"

	plugintools.add_item(action="cambia_hora_arena",url="",title="[COLOR yellow][B]- Cambiar Diferencia Horaria -[/COLOR][/B]",thumbnail="http://image.slidesharecdn.com/1esopresentaciontema1-110109052848-phpapp02/95/tema-1-la-tierra-1-eso-28-728.jpg?cb=1294550960",fanart=fanart,folder=True,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail="http://static.wixstatic.com/media/41d000_0ba0b768e7c98113d7fb91b13075748d.png_srz_980_236_85_22_0.50_1.20_0.00_png_srz", fanart=fanart, folder=False, isPlayable=False)
	plugintools.add_item(action="",url="",title=periodo_agenda,thumbnail="http://s15.postimg.org/bicwnygez/ARENAVISION.jpg", fanart=fanart, folder=False, isPlayable=False)

	lineas = plugintools.find_multiple_matches(data,'<tr><td(.*?)</tr>')

	#***********  Control de Diferencias Horarias DarioMO 15-10-16  *******************
	if not os.path.exists(fich_hora):
		diferencia = "00:00"
		file_hora=open(fich_hora, "w+")
		file_hora.write("00:00")
		file_hora.close()
	else:
		file_hora=open(fich_hora, "r")
		diferencia = file_hora.read()
		file_hora.close()
	#***********  Control de Diferencias Horarias DarioMO 15-10-16  *******************

	diferencia = diferencia + ":00"
	
	i=0
	fecha = "01/01/2001"
	while i < len(lineas)-3:  # xq las 3 última es una línea en blanco
		linea = lineas[i]
		apartados = plugintools.find_multiple_matches(linea,'style="width(.*?)d>')
		lin_item = ""
		cuenta = 0
		cuenta2 = 0
		canales = ""
		canales0=""
		es_fecha = False
		
		for item in apartados:
			texto = plugintools.find_single_match(item,'px">(.*?)</t').replace("SOCCER","Fútbol").replace("<br />"," / ")
			texto = texto.replace("<br />","").replace("FOOTBALL","Rugby Americano").replace("PRESEASON","Pretemporada").replace("OLYMPICS","Olimpicos").replace("BASKETBALL","Baloncesto").replace("SWIMMING","Natación")  # .decode('unicode_escape').encode('utf8')
			cuenta = cuenta + 1
			
			if cuenta == 1:  # Fecha ... 11/08/16... casi siempre, pero cuando les sale de los huevos, ponen el 1º los canales y la fecha el último
				#voy a buscar la fecha y los canales xq van cambiando.
				for item2 in apartados:
					texto = plugintools.find_single_match(item2,'px">(.*?)</t').replace("SOCCER","Fútbol").replace("<br />"," / ")
					texto = texto.replace("<br />","").replace("FOOTBALL","Rugby Americano").replace("PRESEASON","Pretemporada").replace("OLYMPICS","Olimpicos").replace("BASKETBALL","Baloncesto").replace("SWIMMING","Natación")  # .decode('unicode_escape').encode('utf8')
					barra1 = texto[2:3]
					barra2 = texto[5:6]
					plugintools.log("*****************Barras: : "+barra1+"  "+barra2+"********************")
					if barra1 == "/" and barra2 == "/":
						if fecha <> texto:
							fecha = texto
							# Voy a sacar el día de la semana
							# Pero primero voy a corregir que muchas veces ponen el mes y/o el año mal
							fecha_actu=time.strftime("%d/%m/%Y", time.localtime())
							dia_actu = fecha_actu[:2]
							mes_actu = fecha_actu[3:5]
							ano_actu = fecha_actu[6:]
							mes_capullos = fecha[3:5]
							ano_capullos = fecha[6:]
							if mes_actu <> mes_capullos and dia_actu <> "01":
								if mes_actu == "02" and dia_actu <= "27":
									fecha=fecha.replace("/"+mes_capullos+"/", "/"+mes_actu+"/")
								else:
									if mes_actu <> "02" and dia_actu < "30":
										fecha=fecha.replace("/"+mes_capullos+"/", "/"+mes_actu+"/")
							if ano_actu <> ano_capullos and dia_actu+mes_actu <> "31/12" and dia_actu+mes_actu <> "01/01":
								fecha=fecha.replace("/"+ano_capullos, "/"+ano_actu)

							t0=time.strptime(fecha, '%d/%m/%Y')
							
							dia_ing=time.strftime("%A",t0)
							dia_esp = dicdias[dia_ing]

							#Creo una línea
							line_fech = "[COLOR lleyow][B][I]" + dia_esp + ", " + fecha + "[/COLOR][/B][/I]"
							plugintools.add_item(action="",url="",title=line_fech,thumbnail="http://static.wixstatic.com/media/41d000_0ba0b768e7c98113d7fb91b13075748d.png_srz_980_236_85_22_0.50_1.20_0.00_png_srz", fanart=fanart, folder=False, isPlayable=False)
							
					#elif texto.find("]") >= 0:  # son los canales
					#elif "]" in texto:  # son los canales
					#No pregunteis xq, pero ninguna de las 2 formas funciona... el kodi hoy se las pasa x los huevos... vamos a x el 3º intento
					idioma = plugintools.find_single_match(texto,'[(.*?)]')
					if len(idioma) <> 0:  # son los canales... a ver si es verdad :-)
						canales0=texto
						#cuenta = 2
						
			elif cuenta == 2:  # Hora
				#***********  Control de Diferencias Horarias DarioMO 15-10-16  *******************
				hora_esp = texto.replace(" CET","").strip()
				hora_esp = hora_esp + ":00"  # Añado los segundos
				hora_dif = diferencia + ":00"  # Añado los segundos
				lista_esp = hora_esp.split(":")
				lista_dif = diferencia.replace("-","").split(":")

				esp_hora=int(lista_esp[0])
				esp_minuto=int(lista_esp[1])
				esp_segundo=int(lista_esp[2])

				dif_hora=int(lista_dif[0])
				dif_minuto=int(lista_dif[1])
				dif_segundo=int(lista_dif[2])

				formato = "%d-%m-%Y%H:%M:%S"
				h1 = datetime.strptime("12-12-2012"+hora_esp, formato)
				dh = timedelta(hours=dif_hora) 
				dm = timedelta(minutes=dif_minuto)          
				ds = timedelta(seconds=dif_segundo)
				
				
				if "-" in diferencia:  # Hay que restar horas
					resultado1 =h1 - ds
					resultado2 = resultado1 - dm
					resultado = resultado2 - dh
				else:  # Hay que sumar Horas
					resultado1 =h1 + ds
					resultado2 = resultado1 + dm
					resultado = resultado2 + dh

				
				hora="[COLOR lightblue]" + resultado.strftime("%H:%M:%S") + "h[/COLOR]"
				hora = hora.replace(":00h","h")
				#***********  Control de Diferencias Horarias DarioMO 15-10-16  *******************
 
				lin_item = lin_item + "[COLOR red]["+hora+"]   "
				
				

			elif cuenta == 3:  # Deporte
				lin_item = lin_item + "[COLOR orange]("+texto

			elif cuenta == 4:  # Evento
				lin_item = lin_item + "-"+texto.title()+")    "

			elif cuenta == 5:  # Partido
				lin_item = lin_item + "[COLOR green]"+texto.title()+"[/COLOR]"

			elif cuenta == 6:  # or len(canales0) > 0:  # Canales
				if len(canales0) > 0:  # Ya lo han puesto donde les da la gana
					canales = canales0
				else:	
					canales = texto
					
		plugintools.add_item(action="arena_pon_canales",url=canales,title=lin_item,thumbnail="http://s15.postimg.org/bicwnygez/ARENAVISION.jpg", fanart=fanart, folder=True, isPlayable=False)
		i = i + 1
			
def cambia_hora_arena(params):

	if not os.path.exists(fich_hora):
		diferencia = "00:00"
		file_hora=open(fich_hora, "w+")
		file_hora.write("00:00")
		file_hora.close()
	else:
		file_hora=open(fich_hora, "r")
		diferencia = file_hora.read()
		file_hora.close()

	pide = plugintools.keyboard_input(diferencia, 'Introduzca Diferencia (con [COLOR red]Signo Menos[/COLOR] si son a Disminuir) [COLOR green]XX:XX[/COLOR]')
	
	if pide <> diferencia:
		file_hora=open(fich_hora, "w+")
		file_hora.write(pide)
		file_hora.close()
		xbmcgui.Dialog().ok( "- Tenga en Cuenta -" , "Para que el cambio tenga efecto en la Guía, tendrá que salir del Parser y volver a entrar." )

	return

	
		
def arena_pon_canales(params):
	canales = params.get("url")
	title = params.get("title")

	plugintools.add_item(action="",url="",title="[COLOR blue][B]                 ArenaVision[/B]   [I]"+version+"[/I][/COLOR][COLOR yellow][I]    **** byDMax ****[/I][/COLOR]",thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	plugintools.add_item(action="",url="",title=title,thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	canales = ">" + canales.replace("]", "];#>").replace("/","")
	canales_Idioma = plugintools.find_multiple_matches(canales,'>(.*?)#')
	plugintools.log("************Canales1: "+canales+"**************")
	
	for item in canales_Idioma:
		cada_canal = item.split("-")
		
		#En el último quedará el canal y el idioma: "25 [Spa]"
		idioma0 = cada_canal[-1]
		idioma0 = idioma0.replace("[",">").replace("]","<")
		idioma = " [" + plugintools.find_single_match(idioma0,'>(.*?)<') + "]"
		
		for item2 in cada_canal:
			item2 = item2.strip()
			if "[" in item2:  # El último
				#if "S" in item2:  # Es SopCast
				if item2[:1] == "S":  # Es SopCast
					linea = "[COLOR orange]Ver en Canal:   [COLOR lightgreen][B]"+item2+"        [/B][COLOR blue][I](SopCast)[/COLOR][/I]"
				else:
					linea = "[COLOR orange]Ver en Canal:   [COLOR lightgreen][B]"+item2+"        [/B][COLOR red][I](Acestream)[/COLOR][/I]"
				canal0 = item2.replace("[","<")
				canal = plugintools.find_single_match(canal0,'(.*?)<')
			else:
				if "S" in item2:  # Es SopCast
					linea = "[COLOR orange]Ver en Canal:   [COLOR lightgreen][B]"+item2+idioma+"        [/B][COLOR blue][I](SopCast)[/COLOR][/I]"
				else:
					linea = "[COLOR orange]Ver en Canal:   [COLOR lightgreen][B]"+item2+idioma+"        [/B][COLOR red][I](Acestream)[/COLOR][/I]"
				canal = item2

			url = "http://arenavision.in/av"+canal
			plugintools.log("********************URL: "+url+"***********************")	
			url_montada = 'plugin://plugin.video.SportsDevil/?mode=1&amp;item=catcher%3dstreams%26url='+url+'%26referer='+url_ref
			plugintools.add_item(action="runPlugin",url=url_montada,title=linea.replace(";",""),thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=True)
			

			
def arenazaping(params):
	plugintools.add_item(action="",url="",title="[COLOR blue][B]                 ArenaVision[/B]   [I]"+version+"[/I][/COLOR][COLOR yellow][I]    **** byDMax ****[/I][/COLOR]",thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	plugintools.add_item(action="arena_aces",url="",title="[COLOR red][B]-Zaping Canales Acestream[/B][/COLOR]",thumbnail="http://i60.fastpic.ru/big/2013/0919/d0/a8952cb734b26b22d0ed9f09c15c7ad0.jpg",fanart="http://i.imgur.com/IdjjIKU.png",folder=True,isPlayable=False)
	plugintools.add_item(action="arena_sop",url="",title="[COLOR blue][B]-Zaping Canales SopCast[/B][/COLOR]",thumbnail="http://4.bp.blogspot.com/-aI1DjI8Z_2A/VkUgsbxDp3I/AAAAAAAAAtU/8acShCU4OEA/s320/1419590253_sopcast_online.jpg",fanart="http://i.imgur.com/IdjjIKU.png",folder=True,isPlayable=False)

	
def arena_aces(params):
	fanart = params.get("fanart")
	thumbnail = params.get("thumbnail")
	title = "          ·····  " + params.get("title").replace("-","") + "  ·····"

	plugintools.add_item(action="",url="",title="[COLOR blue][B]                 ArenaVision[/B]   [I]"+version+"[/I][/COLOR][COLOR yellow][I]    **** byDMax ****[/I][/COLOR]",thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	plugintools.add_item(action="",url="",title=title,thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	r = requests.get(url)	
	data = r.content
	
	canales = plugintools.find_single_match(data,'active">PORTADA(.*?)/sopcast')
	cada_canal = plugintools.find_multiple_matches(canales,'href=(.*?)/a>')

	i = 0
	while i < len(cada_canal):
		item = cada_canal[i]
		#for item in cada_canal:
		plugintools.log("************Item: "+item+"**************")
		if "/agenda" in item == False and "/acestream" in item == False:
			#23:27:31 T:4228  NOTICE: ************Item: "/av13">ArenaVision 13<**************

			canal = url + plugintools.find_single_match(item,'"(.*?)"')
			titulo = "-Ver ArenaVisión " + plugintools.find_single_match(item,">ArenaVision(.*?)<")

			plugintools.log("************Canal: "+canal+"**************")
			plugintools.log("************Titulo: "+titulo+"**************")
            # "/av4">ArenaVision 4<**************


			url_montada = 'plugin://plugin.video.SportsDevil/?mode=1&amp;item=catcher%3dstreams%26url='+canal+'%26referer='+url_ref
			plugintools.add_item(action="runPlugin",url=url_montada,title=titulo,thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=True)
		i = i + 1	



def arena_sop(params):
	fanart = params.get("fanart")
	thumbnail = params.get("thumbnail")
	title = "          ·····  " + params.get("title").replace("-","") + "  ·····"

	plugintools.add_item(action="",url="",title="[COLOR blue][B]                 ArenaVision[/B]   [I]"+version+"[/I][/COLOR][COLOR yellow][I]    **** byDMax ****[/I][/COLOR]",thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
	plugintools.add_item(action="",url="",title="",thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	plugintools.add_item(action="",url="",title=title,thumbnail=thumbnail, fanart=fanart, folder=False, isPlayable=False)

	r = requests.get(url)	
	data = r.content
	
	canales = plugintools.find_single_match(data,'active"/sopcast(.*?)</ul></li>')
	cada_canal = plugintools.find_multiple_matches(canales,'href=(.*?)/a>')
	
	i = 0
	while i < len(cada_canal):
		item = cada_canal[i]
		#for item in cada_canal:
		canal = url + plugintools.find_single_match(item,'"(.*?)"')
		titulo = "-Ver ArenaVisión " + plugintools.find_single_match(item,">ArenaVision(.*?)<")

		plugintools.log("************Canal: "+canal+"**************")
		plugintools.log("************Titulo: "+titulo+"**************")

		url_montada = 'plugin://plugin.video.SportsDevil/?mode=1&amp;item=catcher%3dstreams%26url='+canal+'%26referer='+url_ref
		plugintools.add_item(action="runPlugin",url=url_montada,title=titulo,thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=True)
		
		i = i + 1


	




