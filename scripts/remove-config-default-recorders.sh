#!/bin/bash -e

hash jq 2>/dev/null || { echo >&2 "I require jq but it's not installed.  Aborting."; exit 1; }
hash aws 2>/dev/null || { echo >&2 "I require aws cli but it's not installed.  Aborting."; exit 1; }

export CONFIGRECORDER=$(aws configservice describe-configuration-recorders | jq .ConfigurationRecorders[].name | tr -d '"')
export DELIVERYCHANNEL=$(aws configservice describe-delivery-channels  | jq .DeliveryChannels[].name | tr -d '"')


if [ -z "$CONFIGRECORDER" ]
  then
      	echo "\$CONFIGRECORDER is empty, so CloudFormation Should Complete OK"
  else
      	echo "\$CONFIGRECORDER $CONFIGRECORDER must be deleted to deploy this CloudFormation Template"
fi

if [ -z "$DELIVERYCHANNEL" ]
  then
      	echo "\$DELIVERYCHANNEL is empty, so CloudFormation Should Complete OK"
  else
      	echo "\$DELIVERYCHANNEL $DELIVERYCHANNEL must be deleted to deploy this CloudFormation Template"
fi


if [ ! -z "$CONFIGRECORDER" ] || [ ! -z "$DELIVERYCHANNEL" ]
  then
	echo "Do you want to Remove them?  Warning this will delete objects, this should be done in a sandbox account!!!"
	echo "Enter 'YES' to delete these objects" 
	read ANSWER
		if [ $ANSWER = "YES" ]
			then
				echo "Deleting ..."
				if [ ! -z "$CONFIGRECORDER" ]; then aws configservice delete-configuration-recorder --configuration-recorder-name $CONFIGRECORDER; fi
				if [ ! -z "$DELIVERYCHANNEL" ]; then aws configservice delete-delivery-channel --delivery-channel-name $DELIVERYCHANNEL; fi
			else
				echo "Doing Nothing & Exiting"
		fi
  else
	echo "AWS Account is clear to deploy CloudFormation Template for this AWSConfig Lab"
fi
