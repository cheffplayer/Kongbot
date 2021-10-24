# All the websocket messages

def connect(wsapp, cfg):
    wsapp.send("<open xmlns='urn:ietf:params:xml:ns:xmpp-framing' to='of1.kongregate.com' version='1.0'/>")
    wsapp.send(f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{cfg['token']}</auth>")
    wsapp.send("<iq type='set' id='_bind_auth_2' xmlns='jabber:client'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>xiff</resource></bind></iq>")
    wsapp.send("<iq type='set' id='_session_auth_2' xmlns='jabber:client'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>")
    wsapp.send("<presence xmlns='jabber:client'><show>chat</show></presence>")
    wsapp.send(f"<presence from='{cfg['username'].lower()}@of1.kongregate.com/xiff' to='287709-ngu-idle-1@conference.of1.kongregate.com/{cfg['username']}' xmlns='jabber:client'><x xmlns='http://jabber.org/protocol/muc'><history seconds='60'/></x><status>[&quot;{cfg['sig']}&quot;,&quot;{cfg['vars']}&quot;,{cfg['extra']}]</status></presence>")

def chatsend(wsapp, cfg, send):
    wsapp.send(f"<message to='287709-ngu-idle-1@conference.of1.kongregate.com' from='{cfg['username'].lower()}@of1.kongregate.com/xiff' type='groupchat' id='02826d44-fc2d-4ddf-885d-339c6e1709ea' xmlns='jabber:client'><body>{str(send)}</body><x xmlns='jabber:x:event'><composing/></x></message>")

def ping(wsapp):
    wsapp.send("<iq type='get' id='32a9b0a3-1d77-4b12-8965-fc809bdb340f:ping' xmlns='jabber:client'><ping xmlns='urn:xmpp:ping'/></iq>")
