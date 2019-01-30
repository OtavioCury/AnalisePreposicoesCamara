#!/bin/bash

for i in {18..10}
do
	curl -X GET "http://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario?ano=20"$i"&tipo=PL" >> PLs_e_PECs/todasPlsPecs.xml

done

for i in {18..10}
do
	curl -X GET "http://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ListarProposicoesVotadasEmPlenario?ano=20"$i"&tipo=PEC" >> PLs_e_PECs/todasPlsPecs.xml

done



