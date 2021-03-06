===================================================================================================================================================================================

E89 - PUSH MESSAGING

===================================================================================================================================================================================

O plugin E89 - PUSH MESSAGING permite enviar notificações push a celulares Android e iOS quando alterações em determinados models são feitas.

O plugin funciona da seguinte maneira:

	1 - O client (Android ou iOS) realiza um post para a url push_messaging/register-device/ enviando um json que contém seu token de identificação e o registration id recebido do Google Cloud Messaging ou APNS.

	2 - O plugin cria um objeto do model Device que associa um registration id com um usuário.

	3 - Sempre que um dos models que geram notificações for modificado (explicado em mais detalhe abaixo), o usuário "proprietário" daquele objeto recebe uma notificação push que indica que é preciso buscar dados novos no servidor.

==================================================================================================================================================================================

Para utilizar o plugin, seguir os passos:

1) Instalar o plugin com pip. Caso ocorra um erro na instalação, é devido ao módulo apns, o qual é uma dependência desse plugin. Nesse caso, é necessário baixar o arquivo zip do módulo apns e instalá-lo manualmente. O módulo deve ser baixado daqui: https://github.com/djacobs/PyAPNs. Em seguida, acessar a pasta pelo terminal e executar python setup.py install

2) No arquivo settings.py, adicionar "e89_push_messaging" na lista de INSTALLED_APPS.

3) Inserir no arquivo settings.py as opções de configuração explicadas em sequência.

4) Inserir urls no arquivo urls.py:

    url(r'', include("e89_push_messaging.urls")),

A única url que será incluída é push_messaging/register_device/.

5) Fazer com que todos os models que gerarão notificações também herdem da classe e89_push_messaging.mixins.PushMixin (explicado abaixo).

6) Rodar ./manage.py migrate para criar a tabela de devices.


OPÇÕES NO ARQUIVO settings.py
===============================

Para funcionamento correto, as seguintes opções devem ser definidas no arquivo settings.py:

	GCM_SEND_MESSAGE_URL
	---------------------

		Url para onde deve ser feito o post de envio de mensagens Android. De acordo com a documentação do Google Cloud Messaging, esse valor deve ser igual a https://android.googleapis.com/gcm/send . Essa opção foi mantida para manter compatibilidade com possíveis alterações em versões futuras.

		Ex: GCM_SEND_MESSAGE_URL = "https://android.googleapis.com/gcm/send"


	GCM_API_KEY
	-----------
		Key da api de comunicação GCM. Esse valor deve ser obtido no Google APIs Console (https://console.developers.google.com). Primeiramente deve ser criado um projeto no Google APIs console e a API Google Cloud Messaging for Android deve ser ativada. Em seguida, deve ser criada uma nova chave de acesso, a qual permite utilizar a API. O valor dessa chave de acesso é o que deve ser utilizado. Para mais informações, seguir o tutorial em: https://developer.android.com/google/gcm/gs.html

		Ex: GCM_API_KEY = "AIzaSyCGrbywoCn6zSgTBrZWQldBjsdaCdXHHeg"


	GCM_SENDER_ID
	--------------
		Identificador do servidor na API GCM. Esse valor equivale ao project-id do projeto criado no Google APIs Console. O sender id não é utilizado no código do plugin, porém como uma boa prática, é aconselhado que seja incluído para que seu valor seja encontrado facilmente, visto que é necessário para implementar o cliente Android. Para mais informações sobre como obter esse valor, seguir o tutorial em: https://developer.android.com/google/gcm/gs.html


		Ex: GCM_SENDER_ID = "740831553735"


	APNS_DEV_CERTIFICATE
	---------------------
		String que contém o caminho até o arquivo do certificado de desenvolvimento do APNS (iOS). Esse certificado será utilizado sempre que no arquivo settings.py a opção DEBUG for igual a True.
		É aconselhado que seja criada uma pasta "apns" dentro da pasta principal do projeto django. Em seguida, pode ser utilizado o código do exemplo abaixo para que o caminho fique sempre relativo.

		Ex: APNS_DEV_CERTIFICATE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apns', 'dev_certificate.pem'))


	APNS_DEV_KEY
	------------
		String que contém o caminho até o arquivo da chave de desenvolvimento do APNS (iOS). Essa chave será utilizada sempre que no arquivo settings.py a opção DEBUG for igual a True.
		É aconselhado que seja criada uma pasta "apns" dentro da pasta principal do projeto django. Em seguida, pode ser utilizado o código do exemplo abaixo para que o caminho fique sempre relativo.

		Ex: APNS_DEV_KEY = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apns', 'dev_key.pem'))


	APNS_PROD_CERTIFICATE
	---------------------
		String que contém o caminho até o arquivo do certificado de produção do APNS (iOS). Esse certificado será utilizado sempre que no arquivo settings.py a opção DEBUG for igual a False.
		É aconselhado que seja criada uma pasta "apns" dentro da pasta principal do projeto django. Em seguida, pode ser utilizado o código do exemplo abaixo para que o caminho fique sempre relativo.


		Ex: APNS_PROD_CERTIFICATE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apns', 'prod_certificate.pem'))


	APNS_PROD_KEY
	-------------
		String que contém o caminho até o arquivo da chave de produção do APNS (iOS). Essa chave será utilizada sempre que no arquivo settings.py a opção DEBUG for igual a False.
		É aconselhado que seja criada uma pasta "apns" dentro da pasta principal do projeto django. Em seguida, pode ser utilizado o código do exemplo abaixo para que o caminho fique sempre relativo.

		Ex: APNS_PROD_KEY = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apns', 'prod_certificate.pem'))


	PUSH_DEVICE_OWNER_MODEL
	-----------------------
		String que indica o model utilizado no atributo "owner" de cada Device. Notação: <app>.<model>.

		Ex: PUSH_DEVICE_OWNER_MODEL = "accounts.CustomUser"


	PUSH_DEVICE_OWNER_IDENTIFIER
	----------------------------
		String que indica o atributo do model "owner" que é utilizado como identificador cada objeto. Esse atributo pode ser o próprio id do elemento ou um token de identificação. Ex: "token", "userprofissional__token". Esse atributo será lido pela view de registro do device, para poder associar o device a um usuário.
		No momento em que for realizado o registro do device, deverá ser feito um post com um json no seguinte formato:

			{
				"<PUSH_DEVICE_OWNER_IDENTIFIER>":"...",
				"registration_id":"...",
				"platform": "..." # "android" ou "ios"
			}

		Por exemplo, se o parâmetro PUSH_DEVICE_OWNER_IDENTIFIER for igual a "user__token" ou "token", o json de registro deverá ser: {"token": "asd","registration_id":"asdasdas"}

    	Ex: PUSH_DEVICE_OWNER_IDENTIFIER = "userprofissional__token"


    PUSH_MODELS
    -----------

    	Dicionário contendo a especificação de quais models deverão gerar uma mensagem push de atualização quando forem salvos ou excluídos. Cada item no dicionário deve possuir o seguinte formato:

    	{
    		...
    		"<app>.<model>":{
    			"owner_attr": "get_owners",
    			"payload_alert": "New item!",
    			"identifier": "identifier",
    			"send_on_save": true
    		},
    		...
    	}

    	- owner_attr: indica qual o atributo do model que representa o owner do device. Esse valor é utilizado para saber qual usuário deve ser notificado quando uma instância desse model é alterada. Caso esse valor seja uma string vazia, todos os usuários serão notificados quando uma alteração ocorrer. Esse valor poderá ser uma função, a qual deverá retornar instâncias dos owners.
    	- payload_alert: mensagem de notificação enviada junto ao push. Utilizada para envio para iOS.
    	- identifier: identifier utilizado na notificação do device. Utilizado para que o device saiba qual tipo de notificação recebeu.
    	- send_on_save: booleano que indica se a notificação deve ser gerada automaticamente sempre que o device for salvo. Default: true. Caso seja especificado false, notificações só serão enviadas quando o método "notify_owners" do objeto for chamado.


    	Ex: PUSH_MODELS = {

			    "news.News":{
			        "owner_attr":"_get_audience",
			        "payload_alert": u"Uma nova notícia foi publicada!",
			        "identifier":"news",
			        "send_on_save":False
			    },

			    "bulletins.Bulletin":{
			        "owner_attr":"_get_audience",
			        "payload_alert": u"Um novo comunicado foi publicado!",
			        "identifier":"bulletins"
			    },

			    "surveys.SurveyToDelete":{
			        "owner_attr":"user_employee",
			        "identifier":"surveys_deleted"
			    },

			    "messaging.Conversation":{
			        "owner_attr":"get_members",
			        "identifier": "conversations",
			        "payload_alert": u"Você recebeu uma nova mensagem!"
			    }
			}


------------------------------------------------------------------------------------------------------------------------
PushMixin
------------------------------------------------------------------------------------------------------------------------

Os models que enviarão push messages de update também deverão herdar da classe PusMixin. Essa classe adiciona os seguintes métodos ao objeto:

	- set_exclude_notify(self,registration_id_list):
		Seta uma lista de registration ids que não deverão ser notificados na próxima vez que o objeto for salvo. É útil para evitar notificar um client que enviou dados que serão salvos no banco mas ao mesmo tempo comunicar outros clients que tenham interesse naquele objeto. Essa lista não é permanente e só será utilizada uma vez quando o objeto for salvo.

	- get_exclude_notify(self):
		Retorna a lista de registration_ids que não serão notificados.

	- set_notify(self,notify):
		Recebe um booleano que indica se, ao salvar o objeto na próxima vez, deverá ser enviada uma notificação push. Útil para objetos compostos, ou seja, um outro objeto possui uma foreign key para o objeto sendo salvo e só se deseja notificar o client quando todos os sub-objetos também tiverem sido salvos.

	- get_notify(self):
		Retorna o booleano que indica se uma notificação push vai ser enviada ou não ao salvar.

------------------------------------------------------------------------------------------------------------------------
Testing
------------------------------------------------------------------------------------------------------------------------

For testing if the right people are receiving push messages, use the function e89_push_messaging.push_tools.mock_push.

Use it in your test cases like this:

	...
	with mock_push(Model) as receiver:
        ...
        self.assertEqual(receiver.notified, set([instance.owner.id]))
    ...



To build the library, run:

python setup.py sdist
