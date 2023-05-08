# Laboratório 2 - Sistemas Distribuídos 2023.1

## Estilo arquitetural

Decidi utilizar o **estilo arquitetural de camadas** com 4 componentes, sendo que um desses componentes serve como uma ponte de comunicação entre os lados do cliente e do servidor. Cada componente será implementado como uma classe de python. 

## Componentes

Lista dos componentes e suas funcionalidades na ordem da camada mais acima até a mais abaixo:

* **Cliente:** Implementa a interface de usuário e envia requisições para o lado do servidor através do componente Socket.
* **Conexão:** Encapsula todo o código para enviar e receber mensagens através de um socket de rede.
* **Servidor:** Recebe e processa as requisições do cliente e envia respostas com os valores do dicionário. Também implementa uma interface para o administrador do servidor.
* **Dicionário:** Implementa o acesso, a remoção e a edição do dicionário assim como a leitura e escrita do arquivo que armazena o dicionário.

## Cliente e Servidor

O lado cliente fica com o componente Cliente enquanto o lado servidor fica com os componentes Servidor e Dicionário. O componente Conexão fica presente em ambos os lados, como é demonstrado no diagrama abaixo.

### Diagrama

![Diagrama](img/diagrama_lab2.png)

## Mensagens

As mensagens que serão enviadas através do componente Conexão tem os quatro primeiros bytes reservados para informar o tamanho da mensagem. Isso permite que os dois lados da conexão saibam quando uma mensagem acaba.

Existem três comandos que o cliente pode enviar ao servidor como mensagem:

* `READ [chave]` - Comando de leitura. O cliente envia esse comando quando quer ler uma entrada do dicionário do servidor. Ao receber esse comando o servidor envia de volta ao cliente uma string com a lista dos valores da entrada `[chave]` do dicionário ou a string `"[]"` caso essa entrada não exista no dicionário.
  
* `WRITE [chave] [valor]` - Comando de escrita. O cliente envia esse comando quando quer adicionar uma entrada no dicionário. Ao receber esse comando o servidor vai alterar o dicionário e vai enviar como resposta a string `"Entrada ([chave],[valor]) adicionada ao dicionario."` ou a string `"Valor '[valor]' adicionado na entrada '[chave]' do dicionario."` dependendo se a entrada `[chave]` já existia no dicionàrio ou não.

* `REMOVE [chave]` - Comando de remoção. O cliente envia esse comando quando quer remover uma entrada do dicionário, porém como ele não possui privilégios para usar esse comando ele não surte efeito. Ao receber esse comando do cliente, o servidor envia de volta a string `"Apenas o administrador pode usar este comando!"`. O servidor pode digitar esse comando na interface de usuário, fazendo com que a entrada `[chave]` do dicionário seja removida, mas ele será processado dentro do próprio servidor e não será enviado através da conexão.
  
O clinte pode também envia uma mensagem de um comando que não é um dos listados acima, porém o servidor respondera com a mensagem `"COMANDO '[comando]' INVALIDO"` indicando que o comando é inválido.

Além disso, existe também o comando `QUIT` que pode ser digitado na interface de usuário tanto pelo cliente quanto pelo servidor para encerrar o programa. Como esse comando é processado sem ser enviado para o outro lado da conexão ele não é considerado uma mensagem.

## Executando o cliente e o servidor

Os programas do cliente e do servidor podem ser executados com os seguintes comandos:

```
python3 servidor.py
python3 cliente.py
```

Ambos utilizam o endereço localhost e a porta 5016 por padrão. Para o caminho do arquivo do dicionário, o servidor usa o arquivo `dict.json` por padrão. Para usar valores costumizados é possível executar os scripts da seguinte forma:

```
python3 servidor.py [endereco] [porta] [arquivo_dicionario]
python3 cliente.py [endereco] [porta]
```