/*
 * DeviantCord 4
 * Copyright (C) 2020-2024  Errite Softworks LLC/ ErriteEpticRikez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
package org.errite.deviantcord.threading;

import java.util.concurrent.*;

public class ExecutorManager {
    private final ThreadPoolExecutor commandExecutor;
    private final ExecutorService rabbitExecutor;
    private final ScheduledExecutorService scheduledExecutor;
    private final ScheduledExecutorService healthCheckExecutor;
    private volatile boolean isRunning = true;

    public ExecutorManager() {
        commandExecutor = new ThreadPoolExecutor(
            8, 20, 60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(2000),
            new DeviantThreadFactory("deviantcord-worker"),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );

        rabbitExecutor = Executors.newSingleThreadExecutor(
            new DeviantThreadFactory("rabbit-worker")
        );

        scheduledExecutor = Executors.newScheduledThreadPool(
            3, new DeviantThreadFactory("scheduled-worker")
        );

        healthCheckExecutor = Executors.newSingleThreadScheduledExecutor(
            new DeviantThreadFactory("health-check-worker")
        );
    }

    public ThreadPoolExecutor getCommandExecutor() { return commandExecutor; }
    public ExecutorService getRabbitExecutor() { return rabbitExecutor; }
    public ScheduledExecutorService getScheduledExecutor() { return scheduledExecutor; }
    public ScheduledExecutorService getHealthCheckExecutor() { return healthCheckExecutor; }
    public boolean isRunning() { return isRunning; }
    public void setRunning(boolean running) { isRunning = running; }

    public void shutdown() {
        System.out.println("Shutting down executor services...");
        isRunning = false;
        
        shutdownExecutor(commandExecutor, "Command");
        shutdownExecutor(rabbitExecutor, "Rabbit");
        shutdownExecutor(scheduledExecutor, "Scheduled");
        shutdownExecutor(healthCheckExecutor, "Health Check");
    }

    private void shutdownExecutor(ExecutorService executor, String name) {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            executor.shutdownNow();
        }
    }
}
