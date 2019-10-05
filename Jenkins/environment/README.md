# Jenkins Debug with Docker






```
version: "3"
services:
  tomcat:
    image: tomcat:8.5.27
    ports:
      - "8080:8080"
      - "5005:5005"
    volumes:
      - ./www:/usr/local/tomcat/webapps:rw
      #- ./conf/server.xml:/usr/local/tomcat/conf/server.xml:ro
    environment:
      TZ: Asia/Shanghai
      JPDA_ADDRESS: 5005
      JPDA_TRANSPORT: dt_socket
    command: ["catalina.sh", "jpda", "run"]
    networks:
      - default

  # 需要nginx、mysql、redis、activemq配置都可以在这里加上

networks:
  default:
```



www下只需要放入war包，启动后，tomcat会自动解压