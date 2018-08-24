#!/usr/bin/python
# -*- coding: utf-8 -*-

## Made by Rgumiel - 2018 ##

import settings

import codecs
import json
import os
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqttPublish
if settings.USE_LEDS:
	import pixels
import sys
from threading import Timer
import time

import logging

logging.basicConfig(
	format='%(asctime)s [%(threadName)s] - [%(levelname)s] - %(message)s',
	level=logging.INFO,
	filename='logs.log',
	filemode='w'
)

OPEN_WORKORDER 				= 'hermes/intent/bobichalton:openWorkorder'
NEXT_STEP 					= 'hermes/intent/bobichalton:nextStep'
STEPS		 				= 'hermes/intent/bobichalton:steps'
PREVIOUS_STEP 				= 'hermes/intent/bobichalton:previousStep'
REPEAT_STEP 				= 'hermes/intent/bobichalton:repeatStep'
ACTIVATE_TIMER 				= 'hermes/intent/bobichalton:activateTimer'

HERMES_ON_HOTWORD 			= 'hermes/hotword/default/detected'
HERMES_START_LISTENING 		= 'hermes/asr/startListening'
HERMES_SAY 					= 'hermes/tts/say'
HERMES_CAPTURED 			= 'hermes/asr/textCaptured'
HERMES_HOTWORD_TOGGLE_ON 	= 'hermes/hotword/toggleOn'

def onConnect(client, userData, flags, rc):
	mqttClient.subscribe(OPEN_WORKORDER)
	mqttClient.subscribe(NEXT_STEP)
	mqttClient.subscribe(STEPS)
	mqttClient.subscribe(PREVIOUS_STEP)
	mqttClient.subscribe(REPEAT_STEP)
	mqttClient.subscribe(ACTIVATE_TIMER)

	mqttClient.subscribe(HERMES_ON_HOTWORD)
	mqttClient.subscribe(HERMES_START_LISTENING)
	mqttClient.subscribe(HERMES_SAY)
	mqttClient.subscribe(HERMES_CAPTURED)
	mqttClient.subscribe(HERMES_HOTWORD_TOGGLE_ON)
	mqttPublish.single('hermes/feedback/sound/toggleOn', payload=json.dumps({'siteId': 'default'}), hostname='127.0.0.1', port=1883)

def onMessage(client, userData, message):
	global lang

	intent = message.topic

	if intent == HERMES_ON_HOTWORD:
		if settings.USE_LEDS:
			leds.wakeup()
		return

	elif intent == HERMES_SAY:
		if settings.USE_LEDS:
			leds.speak()
		return

	elif intent == HERMES_CAPTURED:
		if settings.USE_LEDS:
			leds.think()
		return

	elif intent == HERMES_START_LISTENING:
		if settings.USE_LEDS:
			leds.listen()
		return

	elif intent == HERMES_HOTWORD_TOGGLE_ON:
		if settings.USE_LEDS:
			leds.off()
		return

	global workorder, currentStep, timers, confirm

	payload = json.loads(message.payload)
	sessionId = payload['sessionId']

	if intent == OPEN_WORKORDER:
		if 'slots' not in payload:
			error(sessionId)
			return

		slotWorkorderName = payload['slots'][0]['value']['value'].encode('utf-8')

		if workorder is not None and currentStep > 0:
			if confirm <= 0:
				confirm = 1
				endTalk(sessionId, text=lang['warningWorkorderAlreadyOpen'])
				return
			else:
				for timer in timers:
					timer.cancel()

				timers = {}
				confirm = 0
				currentStep = 0

		if os.path.isfile('./Workorders/{}/{}.json'.format(settings.LANG, slotRecipeName.lower())):
			endTalk(sessionId, text=lang['confirmOpening'].format(payload['slots'][0]['rawValue']))
			currentStep = 0

			file = codecs.open('./Workorders/{}/{}.json'.format(settings.LANG, slotWorkorderNameName.lower()), 'r', encoding='utf-8')
			string = file.read()
			file.close()
			Workorder = json.loads(string)

			time.sleep(2)

			workorderName = workorder['name'] if 'phonetic' not in workorder else workorder['phonetic']
			timeType = lang['workorderTime'] if 'workorderTime' in workorder else lang['waitTime']
			workorderOrWaitTime = workorder['workorderTime'] if 'workorderTime' in workorder else workorder['waitTime']

			say(text=lang['workorderPresentation'].format(
				workorderName,
				workorder['difficulty'],
				workorder['person'],
				workorder['totalTime'],
				workorderOrWaitTime,
				timeType
			))
		else:
			endTalk(sessionId, text=lang['recipeNotFound'])

	elif intent == NEXT_STEP:
		if recipe is None:
			endTalk(sessionId, text=lang['sorryNoRecipeOpen'])
		else:
			if str(currentStep + 1) not in recipe['steps']:
				endTalk(sessionId, text=lang['recipeEnd'])
			else:
				currentStep += 1
				step = recipe['steps'][str(currentStep)]

				ask = False
				if type(step) is dict and currentStep not in timers:
					ask = True
					step = step['text']

				endTalk(sessionId, text=lang['nextStep'].format(step))
				if ask:
					say(text=lang['timeAsk'])



	elif intent == PREVIOUS_STEP:
		if recipe is None:
			endTalk(sessionId, text=lang['sorryNoRecipeOpen'])
		else:
			if currentStep <= 1:
				endTalk(sessionId, text=lang['noPreviousStep'])
			else:
				currentStep -= 1
				step = recipe['steps'][str(currentStep)]

				ask = False
				timer = 0
				if type(step) is dict and currentStep not in timers:
					ask = True
					timer = step['timer']
					step = step['text']

				endTalk(sessionId, text=lang['previousStepWas'].format(step))
				if ask:
					say(text=lang['hadTimerAsk'].format(timer))

	elif intent == REPEAT_STEP:
		if recipe is None:
			endTalk(sessionId, text=lang['sorryNoRecipeOpen'])
		else:
			if currentStep <= 1:
				endTalk(sessionId, text=lang['nothingToSayNotStarted'])
			else:
				step = recipe['steps'][str(currentStep)]
				endTalk(sessionId, text=lang['repeatStep'].format(step))

	elif intent == ACTIVATE_TIMER:
		if recipe is None:
			endTalk(sessionId, text=lang['noTimerNotStarted'])
		else:
			step = recipe['steps'][str(currentStep)]

			if type(step) is not dict:
				endTalk(sessionId, text=lang['notTimerForThisStep'])
			elif currentStep in timers:
				endTalk(sessionId, text=lang['timerAlreadyRunning'])
			else:
				timer = Timer(int(step['timer']), onTimeUp, args=[currentStep, step])
				timer.start()
				timers[currentStep] = timer
				endTalk(sessionId, text=lang['timerConfirm'])


def error(sessionId):
	endTalk(sessionId, lang['error'])

def endTalk(sessionId, text):
	mqttClient.publish('hermes/dialogueManager/endSession', json.dumps({
		'sessionId': sessionId,
		'text': text
	}))

def say(text):
	mqttClient.publish('hermes/dialogueManager/startSession', json.dumps({
		'init': {
			'type': 'notification',
			'text': text
		}
	}))

def onTimeUp(*args, **kwargs):
	global timers
	wasStep = args[0]
	step = args[1]
	del timers[wasStep]
	say(text=lang['timerEnd'].format(step['textAfterTimer']))


mqttClient = None
leds = None
running = True
recipe = None
currentStep = 0
timers = {}
confirm = 0
lang = ''

logger = logging.getLogger('Lucy')
logger.addHandler(logging.StreamHandler())

if __name__ == '__main__':
	logger.info('...My Chef...')

	if settings.USE_LEDS:
		leds = pixels.Pixels()
		leds.off()

	try:
		file = codecs.open('./languages/{}.json'.format(settings.LANG), 'r', encoding='utf-8')
		string = file.read()
		file.close()
		lang = json.loads(string)
	except:
		logger.error('Error loading language file, exiting')
		sys.exit(0)

	mqttClient = mqtt.Client()
	mqttClient.on_connect = onConnect
	mqttClient.on_message = onMessage
	mqttClient.connect('localhost', 1883)
	logger.info(lang['appReady'])
	mqttClient.loop_start()
	try:
		while running:
			time.sleep(0.1)
	except KeyboardInterrupt:
		mqttClient.loop_stop()
		mqttClient.disconnect()
		running = False
	finally:
		logger.info(lang['stopping'])
