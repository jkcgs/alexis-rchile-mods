import asyncio

import discord

from modules.base.command import Command


class Elecciones2017SV(Command):
    url = 'http://www.servelelecciones.cl/data/elecciones_presidente/computo/global/19001.json'
    chans_id = ['381798139428077570', '239609664302481408']

    def __init__(self, bot):
        super().__init__(bot)
        self.channels = []
        for idc in Elecciones2017SV.chans_id:
            self.channels.append(discord.Object(id=idc))

        self.log.debug('Iniciando seguimiento de elecciones')
        self.last = ''
        self.data = {}
        self.name = 'elecciones'

    async def handle(self, message, cmd):
        if self.last == '':
            await cmd.answer('Aún no hay datos disponibles')
            return

        msg = 'con {}/{} mesas escrutadas ({}):\n' \
            .format(self.data['mesasEscrutadas'], self.data['totalMesas'], self.data['totalMesasPorcent'])
        for p in self.data['data']:
            msg += '{}: {} ({})\n'.format(p['a'], p['d'], p['c'])

        await cmd.answer(msg)

    async def task(self):
        await self.bot.wait_until_ready()
        try:
            async with self.http.get(Elecciones2017SV.url) as r:
                if r.status != 200:
                    raise Exception('Wrong status: ' + str(r.status))

                data = await r.json()
                curr_mesas = data['mesasEscrutadas']
                if curr_mesas != self.last:
                    self.last = curr_mesas
                    self.data = data

                    if curr_mesas != '0':
                        msg = '**Nuevo cómputo**, con {}/{} mesas escrutadas ({}):\n' \
                            .format(curr_mesas, data['totalMesas'], data['totalMesasPorcent'])
                        for p in data['data']:
                            msg += '{}: {} ({})\n'.format(p['a'], p['d'], p['c'])

                        for chan in self.channels:
                            await self.bot.send_message(chan, msg)
        except Exception as e:
            if isinstance(e, RuntimeError):
                pass
            self.bot.log.exception(e)
        finally:
            await asyncio.sleep(5)

        if not self.bot.is_closed:
            self.bot.loop.create_task(self.task())
