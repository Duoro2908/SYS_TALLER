import pyodbc
from config import Config
import re

# Lista de clientes parseada del prompt
clientes_raw = """
1	Kelvin Espinoza Ortez Hernández	8576-7242	Lucky 110	110cc
2	Jairo Alexander Talavera Bermúdez	8896-5328	Lucky 110	110cc
3	Wilfredo José Cruz López	8469-1669	SX2 200	200cc
4	Carmen Dolores Bermúdez Pastora	7718-4514	CR4V	250cc
5	Cristhian Omar Salgado Amador	8682-8148	RK125	125cc
6	Rosa Argentina Pavón Membreño	8488-0957	HJ 150S	150cc
7	Uriel Aleman Miranda Téllez	7739-1171	CR4V	250cc
8	Digna Auxiliadora Gaitán Rocha	8478-2489	RKS180	180cc
9	Ronald Iván Talavera Membreño	8546-5787	CR4V	250cc
10	Freddy Manuel Espinoza Zeledón	7798-3930	RKV200	200cc
11	Wilfredo José Membreño Espinoza	7751-8347	RKS180	180cc
12	Reynaldo Antonio Amador Guardián	8937-6311	CR4V	250cc
13	Reyna Isabel Sequeira Calero	8901-0651	Houjue 125	125cc
14	Julio César Talavera Rugama	8462-4731	Houjue 125	125cc
15	Jairo Alexander Baltodano Guevara	7713-2677	RKS180	180cc
16	Walter Ariel Guevara Somarriba	8806-4746	Lucky 110	110cc
17	Esperanza del Rosario Pravia Ortez	8923-4309	HJ 150S	150cc
18	Yolanda Isabel Delgadillo Hernández	7709-7882	SX2 200	200cc
19	Gerson David Duarte Narváez	7891-3619	RKV200	200cc
20	Moisés David Mendoza Aráuz	7869-9854	CR4V	250cc
21	Pedro Pablo Téllez Bermúdez	8824-7510	CR4V	250cc
22	Kelvin Espinoza Baltodano Espinoza	8584-2513	CR4V	250cc
23	Erick Javier Rugama Talavera	8698-0841	CR4V	250cc
24	Melba Johana Bermúdez Cruz	7882-4493	SX3 250	250cc
25	Heydi Carolina Reyes Corea	8687-4016	GE150	150cc
26	Karla Vanessa Salgado Zeledón	8442-7868	HJ 150S	150cc
27	Marlon Ernesto Sandino López	7759-8262	GE150	150cc
28	Uriel Aleman Mendoza Obando	8531-5869	CR4V	250cc
29	Jenny Maritza Somarriba Narváez	8802-5634	SX1-150	150cc
30	Norlan Josué Munguía Mendoza	8933-7543	CR4V	250cc
31	Julio César Vado Zeledón	8614-5868	CR4V	250cc
32	Carlos Alberto Cruz Bermúdez	8494-0196	HJ 150S	150cc
33	Pedro Pablo Sequeira Ubau	7869-3406	KA150	150cc
34	Ivan Mercado Reyes Amador	8556-1595	KA150	150cc
35	Suyapa Concepción Amador Miranda	8665-6482	RKS180	180cc
36	Vicente Alonso Reyes Delgadillo	8499-4680	Lucky 110	110cc
37	Ronald Iván Sequeira Blandón	8777-7387	SX3 250	250cc
38	Elena Marisol Pravia Duarte	8689-5134	Houjue 125	125cc
39	Julio César López Rivas	7737-9176	SX1-150	150cc
40	Flor de María Aguilar Ortez	8876-3201	CR4V	250cc
41	Indiana Lisseth Narváez Sandino	8908-3172	CR4V	250cc
42	Carmen Dolores Pastora Ubau	8779-8687	CR4V	250cc
43	Zeneyda Aracely Rugama Bermúdez	8548-7347	CR4V	250cc
44	Néstor Gabriel Téllez Icaza	8758-1223	Lucky 110	110cc
45	Denis Alberto Ortez Peralta	7866-5876	CR4V	250cc
46	Yader Antonio Munguía Gaitán	7796-7054	RK125	125cc
47	Verónica Yahoska Talavera Delgadillo	8573-4670	KA150	150cc
48	Walter Ariel Amador Somarriba	8929-8069	KA150	150cc
49	Ana Lucía Duarte Osejo	8827-2046	CR4V	250cc
50	Cristhian Omar Hernández Zeledón	8846-4170	CR4V	250cc
51	Yolanda Isabel Obando Membreño	7800-3309	SX3 250	250cc
52	Reynaldo Antonio Tinoco Pravia	7893-7452	HJ 150S	150cc
53	Suyapa Concepción Gaitán Somarriba	8619-0496	CR4V	250cc
54	Julio César Espinoza Blandón	8514-9190	HJ 150S	150cc
55	Zacarías Noel Pravia Pavón	7885-0671	CR4V	250cc
56	Uriel Aleman Corea Roque	8462-8498	CR4V	250cc
57	Yesenia del Socorro Sequeira Amador	8653-1473	KA150	150cc
58	Flor de María Aráuz Pravia	8850-7527	RK125	125cc
59	Harold Enrique Zeledón Icaza	8680-8313	CR4V	250cc
60	Alba Nubia Pastora Membreño	8577-7014	KA150	150cc
61	Elvin Danilo Miranda Pravia	8778-8568	CR4V	250cc
62	Cristhian Omar Icaza Miranda	8631-3518	CR4V	250cc
63	Francis Yamileth Aguilar Peralta	8949-8941	CR4V	250cc
64	Marlene Auxiliadora Membreño Pavón	8440-8240	RK125	125cc
65	Esperanza del Rosario Chavarría Sandino	8471-0947	GE150	150cc
66	Rigoberto Isaías Narváez Guevara	8671-1671	CR4V	250cc
67	Yolanda Isabel López Guardián	8613-1869	RKV200	200cc
68	Isabel Cristina Membreño Gaitán	8877-4964	Lucky 110	110cc
69	Yolanda Isabel Aráuz Delgadillo	7833-4123	SX2 200	200cc
70	Marlon Ernesto Somarriba Salgado	8879-7403	CR4V	250cc
71	Néstor Gabriel Sandino Roque	7834-9361	CR4V	250cc
72	Rosa Argentina Icaza López	7802-4994	SX3 250	250cc
73	Cristhian Omar Sandino Miranda	8848-8771	Houjue 125	125cc
74	Wendy Massiel Delgadillo Hernández	8601-3990	SX2 200	200cc
75	Lissette del Rosario Guardián Mendoza	8478-7429	Houjue 125	125cc
76	Efraín José Duarte Tinoco	8765-5125	SX1-150	150cc
77	Efraín José Chavarría Pravia	8880-7154	CR4V	250cc
78	Walter Ariel Alfaro Salgado	8960-3859	RKS180	180cc
79	Ximena Lucía Membreño Guevara	8548-2477	GE150	150cc
80	Moisés David Téllez Ortez	8448-0861	RKV200	200cc
81	Fabricio José Roque Cruz	8474-8467	RK125	125cc
82	Jenny Maritza Roque Pastora	8463-9821	CR4V	250cc
83	Yader Antonio Zeledón Alfaro	8604-4997	CR4V	250cc
84	Ximena Lucía Talavera Tinoco	8758-8675	SX1-150	150cc
85	Jenny Maritza Guardián Munguía	8560-5766	SX3 250	250cc
86	Rosa Argentina Membreño Mendoza	8489-5171	CR4V	250cc
87	Yesenia del Socorro Salgado Amador	8462-1745	Houjue 125	125cc
88	Urania Migdalia Osejo Duarte	8786-5780	RKV200	200cc
89	Jenny Maritza Corea Reyes	8631-6117	CR4V	250cc
90	Oswaldo Rafael Rivas Mendoza	8704-5562	RK125	125cc
91	Yader Antonio Guardián Reyes	8422-1969	SX1-150	150cc
92	Alba Nubia Blandón López	8574-7407	CR4V	250cc
93	Digna Auxiliadora Somarriba Espinoza	8959-4647	CR4V	250cc
94	Gioconda Esperanza Munguía Tinoco	7836-9594	CR4V	250cc
95	Marlene Auxiliadora Rivas Pravia	8840-9097	CR4V	250cc
96	Marlene Auxiliadora Gaitán Membreño	8733-9421	CR4V	250cc
97	Karla Vanessa Miranda Rugama	7795-2145	SX2 200	200cc
98	Francis Yamileth Aguilar Rocha	8788-4247	CR4V	250cc
99	Marlene Auxiliadora Delgadillo Zeledón	7871-2368	CR4V	250cc
100	Walter Ariel Salgado Bermúdez	7875-4965	GE150	150cc
"""

def insertar_clientes():
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        lineas = clientes_raw.strip().split('\n')
        clientes_insertados = 0
        motos_insertadas = 0

        for idx, linea in enumerate(lineas):
            partes = linea.split('\t')
            if len(partes) >= 5:
                # 0: Numero, 1: Nombre, 2: Teléfono, 3: Modelo, 4: Cilindraje
                nombre = partes[1].strip()
                telefono = partes[2].strip()
                modelo = partes[3].strip()
                
                # Extraer números del cilindraje para guardar como int
                cilindraje_str = partes[4].strip()
                cilindraje_match = re.search(r'\d+', cilindraje_str)
                cilindraje_int = int(cilindraje_match.group()) if cilindraje_match else 0
                
                # Para evitar duplicados por teléfono (muy común)
                cursor.execute("SELECT ClienteID FROM Clientes WHERE Telefono = ?", (telefono,))
                cliente = cursor.fetchone()
                
                if not cliente:
                    # Insertar Cliente
                    identificacion_falsa = f"000-000000-{str(idx+1000).zfill(4)}C"
                    cursor.execute(
                        "INSERT INTO Clientes (Identificacion, NombreCompleto, Telefono, Email) VALUES (?, ?, ?, ?)",
                        (identificacion_falsa, nombre, telefono, f"cliente{idx}@taller.com")
                    )
                    cursor.execute("SELECT @@IDENTITY")
                    cliente_id = cursor.fetchone()[0]
                    clientes_insertados += 1
                else:
                    cliente_id = cliente[0]
                
                # Insertar Moto (asumiendo Marca 'Genesis' o genérica si no sabemos)
                marca = 'Genesis'
                placa_falsa = f"M-{str(idx+1000).zfill(5)}"
                cursor.execute(
                    "INSERT INTO Motocicletas (ClienteID, Placa, Marca, Modelo, Anio, Cilindraje) VALUES (?, ?, ?, ?, ?, ?)",
                    (cliente_id, placa_falsa, marca, modelo, 2023, cilindraje_int)
                )
                motos_insertadas += 1

        conn.commit()
        print(f"Carga Masiva Completada: {clientes_insertados} Clientes nuevos, {motos_insertadas} Motos nuevas.")
        conn.close()
    except Exception as e:
        print(f"Error insertando: {e}")

if __name__ == '__main__':
    insertar_clientes()
