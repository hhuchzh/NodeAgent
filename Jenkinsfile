node {
    checkout scm

    env.DOCKER_API_VERSION="1.23"

    sh "git rev-parse --short HEAD > commit-id"
    tag = readFile('commit-id').replace("\n", "").replace("\r", "")

//    sh "git symbolic-ref --short HEAD > branch-name"
//    branch = readFile('branch-name').replace("\n", "").replace("\r", "")

    appName = "nodeagent"
    registryHost = "475230420162.dkr.ecr.ap-northeast-2.amazonaws.com/"
    imageName = "${registryHost}${appName}:${tag}"
    env.BUILDIMG=imageName
    kubeconfig_stg='/root/kubeconfig_stg'
    kubeconfig_prd2a='/root/kubeconfig_prod_2a'
    kubeconfig_prd2c='/root/kubeconfig_prod_2c'

    stage ('Docker Build') {
        docker.build(appName)
    }

    stage ('Docker Push') {
        docker.withRegistry('https://475230420162.dkr.ecr.ap-northeast-2.amazonaws.com', 'ecr:ap-northeast-2:stg_token') {
        docker.image(appName).push(tag)
        }
    }

    stage ('Deploy to cluster') {
	sh "sed -i 's#${registryHost}${appName}:latest#'$BUILDIMG'#' k8s/deployment.yaml"
	sh "kubectl --kubeconfig=${kubeconfig_stg} replace -f k8s/deployment.yaml"

        shouldPublish = input message: 'Deploy To Product', parameters: [[$class: 'ChoiceParameterDefinition', choices: 'yes\nno', description: '', name: 'Deploy']]
        if(shouldPublish == "yes") {
            echo "Deploy service to Product environment"
            sh "kubectl --kubeconfig=${kubeconfig_prd2a} replace -f k8s/deployment.yaml"
            sh "kubectl --kubeconfig=${kubeconfig_prd2c} replace -f k8s/deployment.yaml"
        }

    }


}

