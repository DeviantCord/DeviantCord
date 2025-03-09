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
package org.errite.deviantcord.sd;

public class commandId {

    public enum Command{
        UpdateInverse,
        UpdateChannel,
        SetupRole,
        DeleteStatus,
        DeleteJournal,
        DeleteFolder,
        AddStatus,
        AddPost,
        AddFolder,
        AddAllFolder,
        NextPage,
        PreviousPage,
        SecurityExploit
    }

    public static Enum<Command> parseCommand(String givenString)
    {
        String commandPrefix = givenString.substring(0, 2);
        switch(commandPrefix){
            case "aa":
                return Command.AddAllFolder;
            case "af":
                return Command.AddFolder;
            case "aj":
                return Command.AddPost;
            case "as":
                return Command.AddStatus;
            case "ds":
                return Command.DeleteStatus;
            case "dj":
                return Command.DeleteJournal;
            case "df":
                return Command.DeleteFolder;
            case "np":
                return Command.NextPage;
            case "pr":
                return Command.PreviousPage;
            case "sr":
                return Command.SetupRole;
            case "uc":
                return Command.UpdateChannel;
            case "ui":
                return Command.UpdateInverse;
            default:
                //If this is thrown, likely an exploit has occured. Someone is manipulating Discord Button Response
                // ID's for DeviantCord at this point. Or either someone forgot to add a command prefix to the
                // parseCommand Method.
                throw new SecurityException("An invalid commandid was received from a Discord Interaction!");

        }

    }
}
